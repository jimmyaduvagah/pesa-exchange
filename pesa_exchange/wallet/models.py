from decimal import Decimal
from django.db import models, transaction
from django.db.models.base import Model
from django.db.models.fields.related import ForeignKey
from pesa_exchange.users.models import User
from pesa_exchange.currency.models import Currency, AbstractBase


TRANSACTION_TYPE = [
    ('W', 'WITHDRAWAL'),
    ('D', 'DEPOSIT'),
    ('T', 'WIRE_TRANSFER'),
]


class Wallet(AbstractBase):
    """A digital wallet model class."""

    owner = models.OneToOneField(User, related_name='account',
        on_delete=models.CASCADE)
    currency_default = models.ForeignKey(Currency,
        related_name='currency', on_delete=models.CASCADE, null=True, blank=True)
    balance = models.FloatField(null=True, blank=True)
    status = models.CharField(null=True, blank=True, max_length=255)



class AccountEntry(AbstractBase):
    """Account entries model."""

    account = models.ForeignKey(
        Wallet, related_name="account_entries", on_delete=models.PROTECT
    )
    amount = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    transaction_type = models.CharField(max_length=1, choices=TRANSACTION_TYPE)


class Transaction(AbstractBase):
    """Holds a reference to a double entry.

    It manages accounting entries by ensuring that double entry is observed.
    """
    def __init__(self, *args, **kwargs):
        """Initialize a transaction with a debit and credit entry."""
        self.dr_entry = kwargs.pop("dr_entry", None)
        self.cr_entry = kwargs.pop("cr_entry", None)

        super().__init__(*args, **kwargs)

    debit_entry = models.ForeignKey(AccountEntry, related_name="debit_account_entry",
                on_delete=models.PROTECT, null=True, blank=True)
    credit_entry = models.ForeignKey(AccountEntry, related_name="credit_account_entry",
                on_delete=models.PROTECT, null=True, blank=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Save a transaction AND it's accompanying entries."""

        self.dr_entry.save()
        self.cr_entry.save()

        self.debit_entry = self.dr_entry
        self.credit_entry = self.cr_entry

        super().save(*args, **kwargs)


# Helper functions
def create_dr_entry(wallet, amount, transaction_type):
    args = {        
        "account": wallet,
        "amount": amount,
        "transaction_type": transaction_type,
    }
    return AccountEntry(**args)


def create_cr_entry(wallet, amount, transaction_type):
    kwargs = {
        "account": wallet,
        "amount": amount,
        "transaction_type": transaction_type,
    }
    return AccountEntry(**kwargs)


def post_transaction(dr_entry, cr_entry):
    """process a transaction."""   
    kwargs = {
        "dr_entry": dr_entry,
        "cr_entry": cr_entry, }
    transaction = Transaction(**kwargs)
    transaction.save()



# When the user registers
# Then create for them a default wallet with zero balance
# Then create a facilitating account for posting entries

# When the user deposits funds
# Then debit money to his wallet
# When he withdraws funds credit his wallet

# example deposit
# dr_entry = create_dr_entry(wallet, currency, amount, transaction_date)
# cr_entry = create_cr_entry(facilitating_wallet_acc, currency, amount, transaction_date)


# # example withdraw
# dr_entry = create_dr_entry(facilitating_wallet_acc, currency, amount, transaction_date)
# cr_entry = create_cr_entry(wallet, currency, amount, transaction_date)


# # example Transfer
# dr_entry = create_dr_entry(wallet_transferee, currency, amount, transaction_date)
# cr_entry = create_cr_entry(wallet_owner, currency, amount, transaction_date)

