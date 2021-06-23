from django import db
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pesa_exchange.wallet.serializer import (WalletSerializer, 
    AccountEntrySerializer, TransactionSerializer, Wallet, AccountEntry,
    Transaction)
from pesa_exchange.wallet.models import (create_cr_entry, 
    create_dr_entry, post_transaction)
from pesa_exchange.currency.models import (get_user_currency_rate, 
    get_usd_amount)

class WalletViewSet(viewsets.ModelViewSet):
    """
    A viewset for Wallet instances.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = WalletSerializer
    queryset = Wallet.objects.all()


class AccountEntryViewSet(viewsets.ModelViewSet):
    """
    A viewset for AccountEntry instances.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = AccountEntrySerializer
    queryset = AccountEntry.objects.all()


class TransactionViewSet(viewsets.ModelViewSet):
    """
    A viewset for Transaction instances.
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
    amount = request.data.get('amount', 0)
    user = request.user
    if request.method == 'POST' and user and amount > 0:
        user_wallet = Wallet.objects.get(owner=user)

        if not user_wallet.currency:
            response_message = {
                "Currency": "Set your default currency in your profile page before transacting"}
            return Response(data=response_message)
        if user_wallet.balance < amount:
            response_message = {
                "Balance":"Your Wallet Balance is lower than the Transaction amount of {}.".format(amount)}
            return Response(data=response_message)

        transaction_type = request.data.get('transaction_type', None)
        rate = get_user_currency_rate(user_wallet.currency_default)
        usd_amount = get_usd_amount(rate, amount)

        if transaction_type == "deposit" or "withdrawal":
            try:
                make_deposit_or_withdrawal(
                    user_wallet, amount, usd_amount, transaction_type)
                serializer = WalletSerializer(data=user_wallet)
                serializer.is_valid(raise_exception=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif transaction_type == "transfer":
            transfer_to = request.data.pop('transfer_to', None)
            receiver_wallet = Wallet.objects.get(owner__email=transfer_to)
            try:
                make_transfer(user_wallet, receiver_wallet, amount, usd_amount)
                serializer = WalletSerializer(data=user_wallet)
                serializer.is_valid(raise_exception=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            response_message = {"WrongTransactionType":"Wrong Transactin Type."}
            return Response(data=response_message)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def make_deposit_or_withdrawal(user_wallet, amount, usd_amount, transaction_type):
    """Helper function for carrying out the actual deposit or withdrawal transactions."""

    facilitating_wallet = Wallet.objects.get(owner__email="facilitatingUser@pesaexchange.com")
    if transaction_type == "deposit":
        dr_entry = create_dr_entry(user_wallet, usd_amount, 'D')
        cr_entry = create_cr_entry(facilitating_wallet, usd_amount, 'W')
        post_transaction(dr_entry, cr_entry)
        user_wallet.balance += amount
        user_wallet.save()
    else:
        dr_entry = create_dr_entry(facilitating_wallet, usd_amount, 'D')
        cr_entry = create_cr_entry(user_wallet, usd_amount, 'W')
        post_transaction(dr_entry, cr_entry)
        user_wallet.balance -= amount
        user_wallet.save()


def make_transfer(user_wallet, receiver_wallet, amount, usd_amount):
    """Helper function for carrying out the actual Transfer transaction."""

    rate = 1
    if receiver_wallet.currency_default:
        rate = get_user_currency_rate(receiver_wallet.currency_default)
    transfer_amount = round(rate * usd_amount, 4)
    dr_entry = create_dr_entry(receiver_wallet, usd_amount, 'D')
    cr_entry = create_cr_entry(user_wallet, usd_amount, 'T')
    post_transaction(dr_entry, cr_entry)
    user_wallet.balance -= amount
    user_wallet.save()
    receiver_wallet.balance -= transfer_amount
    receiver_wallet.save()



