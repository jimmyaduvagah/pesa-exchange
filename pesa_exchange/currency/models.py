import coinoxr
from django.db import models

from pesa_exchange.common.models import AbstractBase, CURRENCY_CODE


class Currency(AbstractBase):
    """Model to hold currencies and codes."""

    country = models.CharField(max_length=100)
    currency_iso_code = models.CharField(max_length=5)
    conversion_rate = models.DecimalField(max_digits=16, decimal_places=4)


def get_user_currency_rate(currency):
    api_key = "d870a9424ea744069b50cebbd3ebcf84"
    rates = coinoxr.Latest().get(base="USD")
    rates = rates.body['rates']
    return rates.get(currency.currency_iso_code, 0)


def get_user_currency_amount(rate, amount):
    if rate > 1:
        return amount * rate
    elif rate < 1:
        return amount / rate
    else:
        return amount


def get_receiver_transfer_amount(rate, sender_amount, receiver_currency):
    usd_amount = 0
    if rate > 1:
        usd_amount = sender_amount / rate
    elif rate < 1:
        usd_amount = sender_amount * rate
    else:
        usd_amount = sender_amount

    receiver_rate = get_user_currency_rate(receiver_currency)
    return get_user_currency_amount(receiver_rate, usd_amount)
