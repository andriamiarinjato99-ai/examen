from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from apps.agencies.models import Agency
from apps.clients.models import Client
from apps.accounts.models import BankAccount
from .services import deposit, withdraw, transfer

class BankingServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="testpass123")
        agency = Agency.objects.create(code="TEST", name="Test", address="Test")
        c1 = Client.objects.create(client_number="C1", first_name="A", last_name="A", national_id="N1", email="a@test.local", phone="1")
        c2 = Client.objects.create(client_number="C2", first_name="B", last_name="B", national_id="N2", email="b@test.local", phone="2")
        self.a1 = BankAccount.objects.create(account_number="A001", client=c1, agency=agency)
        self.a2 = BankAccount.objects.create(account_number="A002", client=c2, agency=agency)

    def test_deposit_and_withdraw(self):
        deposit(self.a1.id, "1000", self.user)
        self.a1.refresh_from_db()
        self.assertEqual(self.a1.balance, Decimal("1000.00"))
        withdraw(self.a1.id, "250", self.user)
        self.a1.refresh_from_db()
        self.assertEqual(self.a1.balance, Decimal("750.00"))

    def test_transfer_is_balanced(self):
        deposit(self.a1.id, "1000", self.user)
        transfer(self.a1.id, self.a2.id, "400", self.user)
        self.a1.refresh_from_db()
        self.a2.refresh_from_db()
        self.assertEqual(self.a1.balance, Decimal("600.00"))
        self.assertEqual(self.a2.balance, Decimal("400.00"))
