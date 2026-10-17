from rest_framework import serializers
from .models import Beneficiary

class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = "__all__"
        read_only_fields = ["created_at"]

    def validate_account_number(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le numéro de compte est obligatoire.")
        return value.strip()
