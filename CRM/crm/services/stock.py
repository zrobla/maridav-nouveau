"""Services de gestion des stocks (Phase 1).

Centralise l'application d'un mouvement de stock sur un lot : recalcul du solde,
mise à jour du statut, garde-fous (pas de sortie supérieure au stock disponible).
Toute écriture passe par ici pour rester cohérente et auditable.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from crm.models import (
    StockLot,
    StockLotStatusChoices,
    StockMovement,
    StockMovementTypeChoices,
    STOCK_MOVEMENT_INBOUND,
    STOCK_MOVEMENT_OUTBOUND,
)


def _to_decimal(value) -> Decimal:
    return Decimal(value or 0)


@transaction.atomic
def apply_stock_movement(movement: StockMovement) -> StockMovement:
    """Applique un mouvement déjà instancié (non encore sauvegardé) sur son lot.

    - Entrée / transfert entrant  : solde += quantité
    - Sortie / perte / transfert sortant : solde -= quantité (refusé si insuffisant)
    - Ajustement d'inventaire : le solde est fixé à la quantité recomptée

    Renseigne `balance_after`, met à jour `lot.quantity_on_hand` et le statut du lot.
    """
    lot = StockLot.objects.select_for_update().get(pk=movement.lot_id)
    qty = _to_decimal(movement.quantity)
    if qty < 0:
        raise ValidationError("La quantité d'un mouvement ne peut pas être négative.")

    current = _to_decimal(lot.quantity_on_hand)

    if movement.movement_type in STOCK_MOVEMENT_INBOUND:
        new_balance = current + qty
    elif movement.movement_type in STOCK_MOVEMENT_OUTBOUND:
        if qty > current:
            raise ValidationError(
                f"Stock insuffisant sur le lot {lot.lot_code} : "
                f"{current} en stock, sortie demandée {qty}."
            )
        new_balance = current - qty
    elif movement.movement_type == StockMovementTypeChoices.AJUSTEMENT:
        # La quantité saisie est le nouveau comptage physique réel.
        new_balance = qty
    else:  # pragma: no cover - garde-fou
        raise ValidationError("Type de mouvement inconnu.")

    movement.balance_after = new_balance
    movement.save()

    lot.quantity_on_hand = new_balance
    # Statut automatique : épuisé à 0, redevient disponible si réapprovisionné.
    if new_balance <= 0 and lot.status not in (
        StockLotStatusChoices.BLOQUE,
        StockLotStatusChoices.QUARANTAINE,
    ):
        lot.status = StockLotStatusChoices.EPUISE
    elif new_balance > 0 and lot.status == StockLotStatusChoices.EPUISE:
        lot.status = StockLotStatusChoices.DISPONIBLE
    lot.save(update_fields=["quantity_on_hand", "status", "updated_at"])

    return movement
