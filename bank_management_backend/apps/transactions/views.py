from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer, DepositSerializer, WithdrawSerializer, TransferSerializer
from .services import deposit, withdraw, transfer

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.select_related("source_account", "destination_account", "performed_by").all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["reference", "description", "source_account__account_number", "destination_account__account_number"]
    filterset_fields = ["transaction_type", "status", "currency", "performed_by"]

    @action(detail=False, methods=["post"], url_path="deposit")
    def make_deposit(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tx = deposit(user=request.user, **serializer.validated_data)
        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="withdraw")
    def make_withdraw(self, request):
        serializer = WithdrawSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tx = withdraw(user=request.user, **serializer.validated_data)
        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="transfer")
    def make_transfer(self, request):
        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tx = transfer(user=request.user, **serializer.validated_data)
        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
