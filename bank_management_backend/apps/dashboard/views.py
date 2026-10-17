from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.models import BankAccount
from apps.clients.models import Client
from apps.transactions.models import Transaction

class StatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        completed = Transaction.objects.filter(status=Transaction.Status.COMPLETED)
        return Response({
            "clients": Client.objects.count(),
            "active_clients": Client.objects.filter(is_active=True).count(),
            "accounts": BankAccount.objects.count(),
            "active_accounts": BankAccount.objects.filter(status=BankAccount.Status.ACTIVE).count(),
            "total_balance": BankAccount.objects.filter(status=BankAccount.Status.ACTIVE).aggregate(v=Sum("balance"))["v"] or 0,
            "transactions": completed.count(),
            "deposits_total": completed.filter(transaction_type=Transaction.Type.DEPOSIT).aggregate(v=Sum("amount"))["v"] or 0,
            "withdrawals_total": completed.filter(transaction_type=Transaction.Type.WITHDRAW).aggregate(v=Sum("amount"))["v"] or 0,
            "transfers_total": completed.filter(transaction_type=Transaction.Type.TRANSFER).aggregate(v=Sum("amount"))["v"] or 0,
            "transaction_counts": list(completed.values("transaction_type").annotate(count=Count("id")).order_by("transaction_type")),
        })
