import coinoxr
from django.db import models

from pesa_exchange.common.models import AbstractBase, CURRENCY_CODE


class Currency(AbstractBase):
    """Model to hold currencies and codes."""

    country = models.CharField(max_length=100)
    currency_iso_code = models.CharField(max_length=5, unique=True)
    conversion_rate = models.DecimalField(
        max_digits=16, decimal_places=4, null=True, blank=True)


def get_user_currency_rate(currency):
    coinoxr.app_id = "d870a9424ea744069b50cebbd3ebcf84"
    rates = coinoxr.Latest().get(base="USD")
    rates = rates.body['rates']
    return rates.get(currency.currency_iso_code, 0)


def get_usd_amount(rate, amount):
    return round(amount / rate, 4)


