from django import db
from django.http import response
from pesa_exchange.users.models import User
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated


from pesa_exchange.wallet.serializer import (WalletSerializer, 
    AccountEntrySerializer, TransactionSerializer, Wallet, AccountEntry,
    Transaction)
from pesa_exchange.wallet.models import (create_cr_entry, 
    create_dr_entry, post_transaction)
from pesa_exchange.currency.models import (get_user_currency_rate, 
    get_user_currency_amount, get_receiver_transfer_amount)

class WalletViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing User instances.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()


class AccountEntryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing User instances.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = AccountEntrySerializer
    queryset = AccountEntry.objects.all()


class TransactionViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing User instances.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()


@api_view(['POST'])
def transact(request):
    """
    function for all transactions a user can make on the system ie Deposit,
    Withdrawal, Transfer.
    """
    if request.method == 'POST' and request.user:
        user = request.user
        user_wallet = Wallet.objects.get(user)
        amount = request.data.get('amount', {})
        rate = get_user_currency_rate(user_wallet.currency)
        amount = get_user_currency_amount(rate, amount)
        transaction_type = request.data.pop('transaction_type', {})
        if transaction_type == "deposit":
            default_user = User.objects.get(email="facilitatingUser@pesaexchange.com")
            facilitating_wallet = Wallet.objects.get(default_user)
            dr_entry = create_dr_entry(user_wallet, amount)
            cr_entry = create_cr_entry(facilitating_wallet, amount)
            try:
                post_transaction(dr_entry, cr_entry)
                user_wallet.balance += amount
                user_wallet.save()
            except Exception:
                return response()

        elif transaction_type == "withdrawal":
            default_user = User.objects.get(email="facilitatingUser@pesaexchange.com")
            facilitating_wallet = Wallet.objects.get(default_user)
            dr_entry = create_dr_entry(facilitating_wallet, amount)
            cr_entry = create_cr_entry(user_wallet, amount)
            try:
                post_transaction(dr_entry, cr_entry)
                user_wallet.balance -= amount
                user_wallet.save()
            except Exception:
                return response()
        else:
            transfer_to = request.data.pop('transfer_to', {})
            transfer_to_user = User.objects.get(email=transfer_to)
            transfer_to_wallet = Wallet.objects.get(owner=transfer_to_user)
            transfer_amount = get_receiver_transfer_amount(rate, amount, 
                transfer_to_wallet.currency)
            dr_entry = create_dr_entry(transfer_to_wallet, transfer_amount)
            cr_entry = create_cr_entry(user_wallet, amount)

            try:
                post_transaction(dr_entry, cr_entry)
                user_wallet.balance -= amount
                user_wallet.save()
                transfer_to_wallet.balance += transfer_amount
                transfer_amount.save()
            except Exception:
                return response()

    
