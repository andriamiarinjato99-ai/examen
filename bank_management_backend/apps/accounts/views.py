from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.clients.models import Client
from .models import BankAccount
from .serializers import BankAccountSerializer


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset =  BankAccount.objects.select_related("client","agency").all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["account_number", "client__first_name", "client__last_name", "client__client_number"]
    filterset_fields = ["status", "account_type", "currency", "agency"]

    def get_queryset(self):
        qs = BankAccount.objects.select_related("client", "agency").order_by("-opened_at")
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()
        # Admin / staff : tout voir
        if user.is_staff or user.is_superuser:
            return qs
        # Client : uniquement ses comptes
        client = Client.objects.filter(user=user).first()
        if client is None and getattr(user, "email", None):
            client = Client.objects.filter(email__iexact=user.email).first()
        if client is None:
            return qs.none()
        return qs.filter(client=client)
