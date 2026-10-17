"""
Inscription publique + profil client (JWT SimpleJWT).
"""
from __future__ import annotations

import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import BankAccount
from apps.agencies.models import Agency
from apps.clients.models import Client
from apps.clients.serializers import ClientSerializer


def _client_number() -> str:
    return f"CL{uuid.uuid4().hex[:8].upper()}"


def _account_number() -> str:
    return f"MG{uuid.uuid4().hex[:16].upper()}"


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Body: first_name, last_name, email, phone, password
    Crée User Django + Client + premier compte bancaire, renvoie JWT.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data or {}
        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        phone = (data.get("phone") or "").strip()
        password = data.get("password") or ""

        errors = {}
        if not first_name:
            errors["first_name"] = "Prénom requis."
        if not last_name:
            errors["last_name"] = "Nom requis."
        if not email or "@" not in email:
            errors["email"] = "E-mail valide requis."
        if not phone:
            errors["phone"] = "Téléphone requis."
        if not password or len(password) < 8:
            errors["password"] = "Mot de passe d'au moins 8 caractères."
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
            return Response(
                {"email": "Un compte existe déjà avec cet e-mail."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Client.objects.filter(email__iexact=email).exists():
            return Response(
                {"email": "Un client existe déjà avec cet e-mail."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )

                agency = Agency.objects.order_by("id").first()
                if agency is None:
                    agency = Agency.objects.create(
                        code="AG001",
                        name="Agence Centrale",
                        address="Siège",
                    )

                national_id = (data.get("national_id") or f"NID-{uuid.uuid4().hex[:10]}").strip()[:40]

                client = Client.objects.create(
                    user=user,
                    client_number=_client_number(),
                    first_name=first_name,
                    last_name=last_name,
                    national_id=national_id,
                    email=email,
                    phone=phone[:30],
                    address=(data.get("address") or "").strip()[:255],
                    is_active=True,
                )

                BankAccount.objects.create(
                    account_number=_account_number(),
                    client=client,
                    agency=agency,
                    account_type=BankAccount.AccountType.CURRENT,
                    balance=Decimal("0.00"),
                    currency="MGA",
                    status=BankAccount.Status.ACTIVE,
                )
        except Exception as exc:
            return Response(
                {"detail": f"Inscription impossible: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "client": ClientSerializer(client).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    """GET /api/auth/me/ — fiche client de l'utilisateur connecté."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        client = Client.objects.filter(user=request.user).first()
        if not client:
            client = Client.objects.filter(email__iexact=request.user.email or "").first()
        if not client:
            return Response({"detail": "Aucune fiche client."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClientSerializer(client).data)
