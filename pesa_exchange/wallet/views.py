from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


from pesa_exchange.wallet.serializer import (WalletSerializer, 
    AccountEntrySerializer, TransactionSerializer, Wallet, AccountEntry,
    Transaction)


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