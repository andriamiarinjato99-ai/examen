from decimal import Decimal
from uuid import uuid4
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.accounts.models import BankAccount
from apps.audit.models import AuditLog
from .models import Transaction

def _reference(prefix):
    return f"{prefix}-{uuid4().hex[:16].upper()}"

@transaction.atomic
def deposit(account_id, amount, user, description=""):
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValidationError("Le montant doit être supérieur à 0.")

    account = BankAccount.objects.select_for_update().get(pk=account_id)
    if account.status != BankAccount.Status.ACTIVE:
        raise ValidationError("Le compte n'est pas actif.")

    account.balance += amount
    account.save(update_fields=["balance"])

    tx = Transaction.objects.create(
        reference=_reference("DEP"),
        transaction_type=Transaction.Type.DEPOSIT,
        destination_account=account,
        amount=amount,
        currency=account.currency,
        description=description,
        performed_by=user,
    )
    AuditLog.objects.create(
        user=user, action=AuditLog.Action.DEPOSIT, entity="BankAccount",
        entity_id=str(account.pk),
        description=f"Dépôt de {amount} {account.currency} sur {account.account_number}",
    )
    return tx

@transaction.atomic
def withdraw(account_id, amount, user, description=""):
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValidationError("Le montant doit être supérieur à 0.")

    account = BankAccount.objects.select_for_update().get(pk=account_id)
    if account.status != BankAccount.Status.ACTIVE:
        raise ValidationError("Le compte n'est pas actif.")
    if account.balance < amount:
        raise ValidationError("Solde insuffisant.")

    account.balance -= amount
    account.save(update_fields=["balance"])

    tx = Transaction.objects.create(
        reference=_reference("WDL"),
        transaction_type=Transaction.Type.WITHDRAW,
        source_account=account,
        amount=amount,
        currency=account.currency,
        description=description,
        performed_by=user,
    )
    AuditLog.objects.create(
        user=user, action=AuditLog.Action.WITHDRAW, entity="BankAccount",
        entity_id=str(account.pk),
        description=f"Retrait de {amount} {account.currency} depuis {account.account_number}",
    )
    return tx

@transaction.atomic
def transfer(source_id, destination_id, amount, user, description=""):
    amount = Decimal(str(amount))
    if amount <= 0:
        raise ValidationError("Le montant doit être supérieur à 0.")
    if source_id == destination_id:
        raise ValidationError("Le compte source et le compte destination doivent être différents.")

    # Ordre déterministe des verrous pour limiter les risques de deadlock.
    first_id, second_id = sorted([int(source_id), int(destination_id)])
    locked = {
        a.pk: a for a in BankAccount.objects.select_for_update().filter(pk__in=[first_id, second_id])
    }
    if len(locked) != 2:
        raise ValidationError("Un des comptes est introuvable.")

    source = locked[int(source_id)]
    destination = locked[int(destination_id)]

    if source.status != BankAccount.Status.ACTIVE or destination.status != BankAccount.Status.ACTIVE:
        raise ValidationError("Les deux comptes doivent être actifs.")
    if source.currency != destination.currency:
        raise ValidationError("Les devises des comptes doivent être identiques.")
    if source.balance < amount:
        raise ValidationError("Solde insuffisant.")

    source.balance -= amount
    destination.balance += amount
    source.save(update_fields=["balance"])
    destination.save(update_fields=["balance"])

    tx = Transaction.objects.create(
        reference=_reference("TRF"),
        transaction_type=Transaction.Type.TRANSFER,
        source_account=source,
        destination_account=destination,
        amount=amount,
        currency=source.currency,
        description=description,
        performed_by=user,
    )
    AuditLog.objects.create(
        user=user, action=AuditLog.Action.TRANSFER, entity="Transaction",
        entity_id=str(tx.pk),
        description=f"Virement de {amount} {source.currency}: {source.account_number} -> {destination.account_number}",
    )
    return tx
