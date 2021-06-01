from rest_framework import serializers
from .models import Stock


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('id','stock_name', 'stock_activity',
                  'stock_sector', 'stock_industry', 'stock_identifier')
