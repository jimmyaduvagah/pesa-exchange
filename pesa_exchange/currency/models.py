from django.db import models

from pesa_exchange.common.models import AbstractBase, CURRENCY_CODE


class Currency(AbstractBase):
    """Model to hold currencies and codes."""

    country = models.CharField(max_length=100)
    currency_iso_code = models.CharField(max_length=5)
    conversion_rate = models.DecimalField(max_digits=16, decimal_places=4)
