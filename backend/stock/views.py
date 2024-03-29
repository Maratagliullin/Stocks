import re

import requests

from bs4 import BeautifulSoup
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from .models import SourceDataCompany, Stock
from .serializers import StockSerializer
from .tasks import get_investing_identify

tz = timezone.get_default_timezone()


def get_data_by_regex(regexp, soup):
    match_string = soup.find('div', text=re.compile(r'\b{}'.format(regexp)))
    if not match_string is None:
        return match_string.find_next('div', class_=re.compile('value-.*')).text.strip()
    else:
        return "Данные отсутсвуют"


class StockViews(APIView):

    # Проверка тикера на сушествование
    @transaction.non_atomic_requests
    def get_tiker_status(self, stock):
        try:
            response_tradingview = requests.get(
                "https://ru.tradingview.com/symbols/"+stock+"/")

            stock_ticker = re.search('(?<=/symbols/).*?(?=/)',
                                     response_tradingview.url)
            if response_tradingview.status_code != 404:
                soup_tradingview = BeautifulSoup(
                    response_tradingview.text, 'html.parser')
                stock_name = soup_tradingview.find(
                    'h1')

                stock_sector = get_data_by_regex(
                    'Сектор', soup_tradingview)
                stock_industry = get_data_by_regex(
                    'Отрасль', soup_tradingview)

                stock_name = stock_name.text
                return ({'status': 'found', 'message': 'Акция найдена', 'tradingview_dentifier': response_tradingview.url, 'stock_ticker': stock_ticker.group(0), 'stock_name': stock_name, 'stock_sector': stock_sector, 'stock_industry': stock_industry})
            else:
                return ({'status': 'not_found', 'message': 'Акция не найдена', 'tradingview_dentifier': response_tradingview.url, 'stock_ticker': stock_ticker.group(0)})
        except requests.exceptions.ReadTimeout:
            return ({'status': 'connection_error', 'message': 'Превышение времени ожидания ответа'})

        except requests.exceptions.ConnectTimeout:
            return ({'status': 'connection_error', 'message': 'Время ожидания запроса истекло при попытке подключения к удаленному серверу'})

        except requests.exceptions.ConnectionError:
            return ({'status': 'connection_error', 'message': 'Соединение с интернетом отсутсвует'})

    # обработка POST add ticker
    def post(self, request):
        if request.data['stock']:

            # Извлекаем тикеры
            tickers = []
            data = request.data['stock'].split('\n')
            saved_tiker = []
            for stock_ticker in data:
                if stock_ticker:
                    ticker_status = self.get_tiker_status(stock_ticker)

                    # Если тикер найден
                    if ticker_status['status'] == 'found':

                        # Проверка на дубликат
                        try:
                            found_stock_name = Stock.objects.get(
                                stock_name=ticker_status['stock_name'])

                        except Stock.DoesNotExist:
                            found_stock_name = None

                        # Дубликат наден
                        if found_stock_name != None:
                            tickers.append(
                                {'status': 'dublicate', 'stock_ticker': ticker_status['stock_ticker'], 'message': 'Идентификатор существует'})
                        else:
                            # Сохраним в базе найденный тикер
                            with transaction.atomic():
                                s = Stock(
                                    stock_name=ticker_status['stock_name'],
                                    stock_sector=ticker_status['stock_sector'],
                                    stock_industry=ticker_status['stock_industry'],
                                    stock_activity=True,
                                    tradingview_dentifier=ticker_status['tradingview_dentifier'],
                                    stock_ticker=ticker_status['stock_ticker'],
                                )
                                s.save()

                            # Проверка на сохранение в базе?
                            if (s.pk):
                                saved_tiker.append(s.pk)
                                tickers.append(ticker_status)
                    else:
                        # Тикер не найден
                        tickers.append(ticker_status)
            if saved_tiker:
                get_investing_identify.apply_async(
                    countdown=30)

            if not tickers:
                raise ValidationError(
                    [{'status': 'empty_value', 'message': 'Идентификаторы акции должны быть заполнены'}])
            else:
                return Response(tickers)
        else:
            raise ValidationError(
                [{'status': 'empty_value', 'message': 'Идентификаторы акции должны быть заполнены'}])

    # Обработка GET get ticker
    def get(self, request):
        queryset = Stock.objects.all().order_by('stock_name')
        serializer = StockSerializer(queryset, many=True)
        return Response(serializer.data)

    # Обработка DELETE get ticker
    def delete(self, request, id, format=None):
        with transaction.atomic():
            Stock.objects.filter(
                id=id).update(stock_activity=False)

        return Response(status=status.HTTP_204_NO_CONTENT)

    # Обработка DELETE get ticker
    def put(self, request, id, format=None):
        with transaction.atomic():
            Stock.objects.filter(
                id=id).update(stock_activity=True)

        return Response(status=status.HTTP_204_NO_CONTENT)


def index(request):
    return HttpResponse("Hello, world.")


@api_view(('GET',))
def get_ticker_id(self, ticker):
    queryset = Stock.objects.filter(
        stock_ticker=ticker)
    serializer = StockSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(('GET',))
def get_ticker_data(self, ticker):
    data = {}
    queryset = SourceDataCompany.objects.filter(
        stock_ticker=ticker)
    Tradingview_data = SourceDataCompany.objects.filter(
        stock_ticker=ticker, source='Tradingview').order_by('-date')[:1]
    if Tradingview_data:
        data['tradingview'] = {
            'tradingview_data_json_value': Tradingview_data[0].json_value,
            'tradingview_data_date': Tradingview_data[0].date.astimezone(tz).strftime("%d/%m/%Y %H:%M:%S")
        }
    else:
        data['tradingview'] = {
            'tradingview_data_json_value': 'Данные отсутствуют',
            'tradingview_data_date': 'Данные отсутствуют',
        }

    Investing_data = SourceDataCompany.objects.filter(
        stock_ticker=ticker, source='Investing').order_by('-date')[:1]

    if Investing_data:
        data['investing'] = {
            'investing_data_json_value': Investing_data[0].json_value,
            'investing_data_date': Investing_data[0].date.astimezone(tz).strftime("%d/%m/%Y %H:%M:%S")
        }
    else:
        data['investing'] = {
            'investing_data_json_value': 'Данные отсутствуют',
            'investing_data_date': 'Данные отсутствуют',
        }
    return Response(data)
