from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.agencies.views import AgencyViewSet
from apps.clients.views import ClientViewSet
from apps.accounts.views import BankAccountViewSet
from apps.beneficiaries.views import BeneficiaryViewSet
from apps.employees.views import EmployeeViewSet
from apps.transactions.views import TransactionViewSet
from apps.audit.views import AuditLogViewSet

router = DefaultRouter()
router.register("agencies", AgencyViewSet)
router.register("clients", ClientViewSet)
router.register("accounts", BankAccountViewSet)
router.register("beneficiaries", BeneficiaryViewSet)
router.register("employees", EmployeeViewSet)
router.register("transactions", TransactionViewSet, basename="transactions")
router.register("audit", AuditLogViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("apps.dashboard.urls")),
]
