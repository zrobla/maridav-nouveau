from __future__ import annotations

import json
import logging

from django.core.management.base import BaseCommand, CommandError

from crm.services.observability import build_observability_summary

observability_logger = logging.getLogger("crm.observability.alerts")


class Command(BaseCommand):
    help = "Calcule un snapshot observabilité (API + SLA) et émet les alertes actives."

    def add_arguments(self, parser):
        parser.add_argument(
            "--window-minutes",
            type=int,
            default=None,
            help="Fenêtre de calcul des métriques API (en minutes).",
        )
        parser.add_argument(
            "--fail-on-alert",
            action="store_true",
            help="Retourne un code d'erreur s'il existe au moins une alerte.",
        )

    def handle(self, *args, **options):
        window_minutes = options["window_minutes"]
        summary = build_observability_summary(window_minutes=window_minutes)

        self.stdout.write(
            self.style.SUCCESS(
                f"Observability health={summary['health']} "
                f"(alerts={len(summary['alerts'])}, requests={summary['api']['requests']})."
            )
        )
        self.stdout.write(json.dumps(summary, ensure_ascii=False))

        for alert in summary["alerts"]:
            severity = (alert.get("severity") or "warning").upper()
            code = alert.get("code") or "unknown"
            message = alert.get("message") or ""
            value = alert.get("value")
            threshold = alert.get("threshold")
            line = f"[{severity}] {code}: {message} (value={value}, threshold={threshold})"
            if severity == "CRITICAL":
                observability_logger.error(line)
                self.stderr.write(self.style.ERROR(line))
            else:
                observability_logger.warning(line)
                self.stdout.write(self.style.WARNING(line))

        if options["fail_on_alert"] and summary["alerts"]:
            raise CommandError(f"{len(summary['alerts'])} alerte(s) observabilité active(s).")
