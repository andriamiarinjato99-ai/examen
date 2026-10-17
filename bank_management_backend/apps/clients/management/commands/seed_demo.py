from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.agencies.models import Agency
from apps.clients.models import Client
from apps.employees.models import Employee
from apps.accounts.models import BankAccount

class Command(BaseCommand):
    help = "Crée un jeu de données de démonstration."

    def handle(self, *args, **kwargs):
        admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@bank.local", "first_name": "Admin", "last_name": "Bank"})
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Admin123!")
        admin.save()

        agency, _ = Agency.objects.get_or_create(code="AG001", defaults={"name": "Agence Centrale", "address": "Antananarivo"})
        employee, _ = Employee.objects.get_or_create(
            user=admin, defaults={"employee_number": "EMP001", "agency": agency, "role": Employee.Role.ADMIN}
        )
        employee.agency = agency
        employee.role = Employee.Role.ADMIN
        employee.save()

        client, _ = Client.objects.get_or_create(
            client_number="CL000001",
            defaults={
                "first_name": "Jean", "last_name": "Rakoto", "national_id": "NID000001",
                "email": "jean@example.com", "phone": "0340000000"
            }
        )
        BankAccount.objects.get_or_create(
            account_number="MG000000000000000001",
            defaults={"client": client, "agency": agency, "account_type": "SAVINGS", "currency": "MGA"}
        )
        BankAccount.objects.get_or_create(
            account_number="MG000000000000000002",
            defaults={"client": client, "agency": agency, "account_type": "CURRENT", "currency": "MGA"}
        )

        self.stdout.write(self.style.SUCCESS("Données de démonstration créées."))
        self.stdout.write("Admin JWT: username=admin / password=Admin123!")
