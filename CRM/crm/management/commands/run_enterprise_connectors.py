"""Run enterprise connector processing loop (outbox + inbox)."""

from __future__ import annotations

import json
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from crm.services.integrations import process_inbox_events, process_outbox_events


def _parse_connector_codes(raw: str) -> list[str]:
    values = [value.strip() for value in (raw or "").split(",")]
    return [value for value in values if value]


class Command(BaseCommand):
    help = "Exécute le cycle des connecteurs enterprise (outbox/inbox, retries et DLQ)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--connectors",
            default="",
            help="Liste optionnelle de connecteurs (codes séparés par virgules).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Nombre maximum d'événements traités par file (outbox/inbox).",
        )
        parser.add_argument(
            "--outbox-only",
            action="store_true",
            help="Ne traite que la file outbox.",
        )
        parser.add_argument(
            "--inbox-only",
            action="store_true",
            help="Ne traite que la file inbox.",
        )
        parser.add_argument(
            "--at",
            default="",
            help="Horodatage ISO optionnel (ex: 2026-02-26T12:00:00+00:00).",
        )
        parser.add_argument(
            "--fail-on-error",
            action="store_true",
            help="Retourne un code d'erreur si des événements restent en erreur.",
        )

    def handle(self, *args, **options):
        connector_codes = _parse_connector_codes(options.get("connectors", ""))
        limit = max(1, int(options.get("limit") or 100))
        outbox_only = bool(options.get("outbox_only"))
        inbox_only = bool(options.get("inbox_only"))

        if outbox_only and inbox_only:
            raise CommandError("Les options --outbox-only et --inbox-only sont mutuellement exclusives.")

        now = timezone.now()
        raw_at = (options.get("at") or "").strip()
        if raw_at:
            parsed = datetime.fromisoformat(raw_at)
            if parsed.tzinfo is None:
                raise CommandError("L'option --at doit inclure un fuseau horaire.")
            now = parsed

        payload = {"timestamp": now.isoformat(), "outbox": {}, "inbox": {}}
        if not inbox_only:
            payload["outbox"] = process_outbox_events(limit=limit, connector_codes=connector_codes, now=now)
        if not outbox_only:
            payload["inbox"] = process_inbox_events(limit=limit, connector_codes=connector_codes, now=now)

        self.stdout.write(
            self.style.SUCCESS(
                "Enterprise connector cycle OK "
                f"(outbox_delivered={payload['outbox'].get('delivered', 0)}, "
                f"outbox_dead={payload['outbox'].get('dead', 0)}, "
                f"inbox_handled={payload['inbox'].get('handled', 0)}, "
                f"inbox_dead={payload['inbox'].get('dead', 0)})."
            )
        )
        self.stdout.write(json.dumps(payload, ensure_ascii=False))

        if options.get("fail_on_error"):
            outbox_errors = payload["outbox"].get("errors", 0) + payload["outbox"].get("dead", 0)
            inbox_errors = payload["inbox"].get("errors", 0) + payload["inbox"].get("dead", 0)
            if outbox_errors or inbox_errors:
                raise CommandError(
                    "Enterprise connectors run completed with unrecovered errors "
                    f"(outbox={outbox_errors}, inbox={inbox_errors})."
                )
