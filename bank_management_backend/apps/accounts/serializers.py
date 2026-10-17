import uuid
from rest_framework import serializers
from apps.agencies.models import Agency
from apps.clients.models import Client
from .models import BankAccount


def _generate_account_number() -> str:
    return f"MG{uuid.uuid4().hex[:16].upper()}"


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"
        read_only_fields = [
            "id",
            "account_number",
            "client",
            "agency",
            "balance",
            "status",
            "opened_at",
        ]

    def validate(self, attrs):
        if attrs.get("status") == BankAccount.Status.CLOSED and self.instance and self.instance.balance != 0:
            raise serializers.ValidationError(
                "Un compte ne peut être fermé que si son solde est nul."
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        client = None
        if user and user.is_authenticated:
            client = Client.objects.filter(user=user).first()
            if client is None and getattr(user, "email", None):
                client = Client.objects.filter(email__iexact=user.email).first()

        if client is None:
            raise serializers.ValidationError(
                {"detail": "Aucun profil client lié à votre compte. Réinscrivez-vous ou contactez le support."}
            )

        agency = Agency.objects.order_by("id").first()
        if agency is None:
            agency = Agency.objects.create(
                code="AG001",
                name="Agence Centrale",
                address="Siège",
            )

        # Numéro unique
        for _ in range(5):
            number = _generate_account_number()
            if not BankAccount.objects.filter(account_number=number).exists():
                break
        else:
            number = _generate_account_number()

        validated_data["account_number"] = number
        validated_data["client"] = client
        validated_data["agency"] = agency
        validated_data.setdefault("status", BankAccount.Status.ACTIVE)
        validated_data.setdefault("account_type", BankAccount.AccountType.CURRENT)
        validated_data.setdefault("currency", "MGA")

        return super().create(validated_data)
