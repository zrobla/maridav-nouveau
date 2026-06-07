"""Exécute l'orchestration SLA (escalades + actions automatiques)."""

from __future__ import annotations

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from crm.services.governance import refresh_sla_escalations


class Command(BaseCommand):
    help = (
        "Rafraîchit les escalades SLA et déclenche les actions automatiques "
        "(notifications internes + tâches SLA)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--at",
            dest="at",
            default="",
            help="Horodatage ISO facultatif (ex: 2026-02-26T08:30:00+00:00) pour forcer l'instant d'exécution.",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        at_raw = (options.get("at") or "").strip()
        if at_raw:
            parsed = datetime.fromisoformat(at_raw)
            if parsed.tzinfo is None:
                raise CommandError("L'horodatage --at doit inclure un fuseau horaire.")
            now = parsed

        metrics = refresh_sla_escalations(now=now)
        self.stdout.write(
            self.style.SUCCESS(
                "SLA orchestration OK "
                f"(created={metrics['created']}, resolved={metrics['resolved']}, "
                f"notifications={metrics['notifications']}, tasks_created={metrics['tasks_created']})."
            )
        )
