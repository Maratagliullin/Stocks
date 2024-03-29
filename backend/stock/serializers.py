from rest_framework import serializers

from .models import SourceDataCompany, Stock


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('id', 'stock_name', 'stock_activity',
                  'stock_sector', 'stock_industry', 'investing_dentifier', 'tradingview_dentifier', 'stock_ticker')


class SourceDataCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceDataCompany
        fields = ('stock_ticker', 'date', 'source_url',
                  'source', 'json_value')

