from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Agency
from .serializers import AgencySerializer

class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all().order_by("code")
    serializer_class = AgencySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["code", "name", "address"]
    filterset_fields = ["is_active"]
