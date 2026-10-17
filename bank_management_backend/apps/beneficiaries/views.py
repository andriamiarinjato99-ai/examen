from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Beneficiary
from .serializers import BeneficiarySerializer

class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.all().order_by("-created_at")
    serializer_class = BeneficiarySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["name", "account_number", "bank_name"]
    filterset_fields = ["owner", "is_active"]
