"""Build an operational WaasPlus PackPlus client kit."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


SECTOR_PACKS: dict[str, dict[str, object]] = {
    "services_b2b": {
        "priority": 1,
        "default_funnels": ["request_demo", "quote", "consultation_call"],
        "kpi_focus": ["lead_to_meeting_rate", "proposal_rate", "win_rate"],
    },
    "health_wellness": {
        "priority": 1,
        "default_funnels": ["appointment", "service_quote", "whatsapp_followup"],
        "kpi_focus": ["appointment_conversion", "no_show_rate", "response_sla"],
    },
    "education_training": {
        "priority": 1,
        "default_funnels": ["application", "admission_followup", "enrollment"],
        "kpi_focus": ["application_completion", "enrollment_conversion", "cohort_fill_rate"],
    },
    "real_estate_construction": {
        "priority": 2,
        "default_funnels": ["project_inquiry", "property_lead", "quote_request"],
        "kpi_focus": ["qualified_project_leads", "cycle_time", "close_rate"],
    },
    "trade_logistics": {
        "priority": 2,
        "default_funnels": ["quotation_request", "service_inquiry", "account_opening"],
        "kpi_focus": ["quote_response_time", "quote_to_order_rate", "repeat_demand_rate"],
    },
    "ngo_institution": {
        "priority": 3,
        "default_funnels": ["project_call", "donor_contact", "publication_engagement"],
        "kpi_focus": ["submission_compliance", "stakeholder_response_sla", "engagement_rate"],
    },
    "fmcg_multi_species": {
        "priority": 1,
        "default_funnels": ["inbound_qualification", "opportunity_pipeline", "order_execution"],
        "kpi_focus": ["inbound_conversion", "pipeline_value", "sla_overdue_rate"],
    },
}


def _slugify(value: str) -> str:
    candidate = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower())
    candidate = candidate.strip("-")
    return candidate or "client"


def _safe_copy(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _render_onboarding_yaml(payload: dict[str, object]) -> str:
    return (
        f'client_name: "{payload["client_name"]}"\n'
        f'tenant_slug: "{payload["tenant_slug"]}"\n'
        f'tenant_display_name: "{payload["tenant_display_name"]}"\n'
        f'crm_platform_name: "{payload["crm_platform_name"]}"\n'
        f'primary_domain: "{payload["primary_domain"]}"\n'
        "public_domains:\n"
        f'  - "{payload["primary_domain"]}"\n'
        f'  - "www.{payload["primary_domain"]}"\n'
        f'crm_domain: "{payload["crm_domain"]}"\n'
        f'cookie_domain: "{payload["cookie_domain"]}"\n'
        "cors_allowed_origins:\n"
        f'  - "https://{payload["primary_domain"]}"\n'
        f'  - "https://{payload["crm_domain"]}"\n'
        "csrf_trusted_origins:\n"
        f'  - "https://{payload["primary_domain"]}"\n'
        f'  - "https://{payload["crm_domain"]}"\n'
        f'target_environment: "{payload["target_environment"]}"\n'
        f'tls_ready: {"true" if payload["target_environment"] == "prod" else "false"}\n'
        'production_database: "postgresql"\n'
        f'sector_pack: "{payload["sector_pack"]}"\n'
        f'website_template: "{payload["website_template"]}"\n'
        "tenant_branding:\n"
        f'  logo_path: "{payload["brand_logo"]}"\n'
        f'  logo_alt: "{payload["brand_logo_alt"]}"\n'
        f'  sidebar_subtitle: "{payload["brand_sidebar_subtitle"]}"\n'
        f'  platform_tagline: "{payload["crm_platform_tagline"]}"\n'
        "security_cookie_names:\n"
        f'  access_cookie: "{payload["auth_cookie_access"]}"\n'
        f'  refresh_cookie: "{payload["auth_cookie_refresh"]}"\n'
        f'  csrf_cookie: "{payload["csrf_cookie_name"]}"\n'
        "sector_constraints:\n"
        '  - "none"\n'
        "initial_admin_users:\n"
        '  - full_name: "to_define"\n'
        '    email: "to_define@example.com"\n'
        '    role: "Direction Generale"\n'
    )


def _render_env_example(payload: dict[str, object]) -> str:
    primary_domain = str(payload["primary_domain"])
    crm_domain = str(payload["crm_domain"])
    cookie_domain = str(payload["cookie_domain"])
    template_name = str(payload["website_template"])
    return "\n".join(
        [
            "DJANGO_DEBUG=False",
            "DJANGO_SECRET_KEY=change-me",
            f"DJANGO_ALLOWED_HOSTS={primary_domain},www.{primary_domain},{crm_domain}",
            f"DJANGO_SITE_PUBLIC_HOSTS={primary_domain},www.{primary_domain}",
            f"DJANGO_SITE_CRM_HOSTS={crm_domain}",
            f"DJANGO_WEBSITE_TEMPLATE={template_name}",
            f"CRM_TENANT_SLUG={payload['tenant_slug']}",
            f"CRM_TENANT_LEGAL_NAME={payload['tenant_legal_name']}",
            f"CRM_TENANT_DISPLAY_NAME={payload['tenant_display_name']}",
            f"CRM_PLATFORM_NAME={payload['crm_platform_name']}",
            f"CRM_PLATFORM_TAGLINE={payload['crm_platform_tagline']}",
            f"CRM_BRAND_LOGO={payload['brand_logo']}",
            f"CRM_BRAND_LOGO_ALT={payload['brand_logo_alt']}",
            f"CRM_BRAND_SIDEBAR_SUBTITLE={payload['brand_sidebar_subtitle']}",
            f"DJANGO_CORS_ALLOWED_ORIGINS=https://{primary_domain},https://{crm_domain}",
            f"DJANGO_CSRF_TRUSTED_ORIGINS=https://{primary_domain},https://{crm_domain}",
            "DJANGO_COOKIE_SECURE=True",
            "API_SECURITY_STRICT_MODE=True",
            "API_PUBLIC_THROTTLE_PROFILE=medium",
            "DJANGO_SECURE_SSL_REDIRECT=True",
            "DJANGO_SECURE_HSTS_SECONDS=31536000",
            "DJANGO_SESSION_COOKIE_SAMESITE=Lax",
            "DJANGO_CSRF_COOKIE_SAMESITE=Lax",
            f"AUTH_COOKIE_DOMAIN={cookie_domain}",
            f"AUTH_COOKIE_ACCESS={payload['auth_cookie_access']}",
            f"AUTH_COOKIE_REFRESH={payload['auth_cookie_refresh']}",
            f"CSRF_COOKIE_NAME={payload['csrf_cookie_name']}",
            f"WAGTAILADMIN_BASE_URL=https://{crm_domain}",
            "DJANGO_ENTERPRISE_CONNECTORS_LOG_LEVEL=INFO",
            "ERP_COMPTA_API_KEY=",
            "TELEPHONY_HMAC_SECRET=",
            "OBS_METRICS_WINDOW_MINUTES=5",
            "OBS_ALERT_5XX_RATE_PCT=5",
            "SENTRY_DSN=",
            "",
        ]
    )


def _render_delivery_checklist(payload: dict[str, object]) -> str:
    return "\n".join(
        [
            "# Delivery Checklist - WaasPlus PackPlus",
            "",
            "## 1) Intake",
            "- [ ] Client intake YAML validated.",
            "- [ ] Domain and CRM host approved.",
            "- [ ] Sector pack and website template approved.",
            "",
            "## 2) Platform setup",
            "- [ ] Environment variables applied.",
            "- [ ] Migrations and static collect executed.",
            "- [ ] `setup_roles` executed.",
            "- [ ] `setup_enterprise_connectors` executed.",
            "",
            "## 3) Validation gates",
            "- [ ] `python manage.py check` green.",
            "- [ ] `python manage.py test -v 1` green.",
            "- [ ] Public form to CRM flow validated.",
            "- [ ] Media file access validated (`/media/*` does not fall through public catch-all).",
            "- [ ] CRM login on target domain validated.",
            "- [ ] SLA/Observability/Enterprise schedulers enabled.",
            "",
            "## 4) Go-live readiness",
            "- [ ] Rollback plan documented.",
            "- [ ] Runbooks delivered to ops.",
            "- [ ] UAT sign-off collected.",
            "",
            "## 5) Export",
            "- [ ] Final client kit assembled.",
            "- [ ] Final kit moved to `/home/kayz/RESTUCTURATION-TECH&WEB/Waas` at project closure.",
            "",
            "## Context",
            f"- client_name: `{payload['client_name']}`",
            f"- primary_domain: `{payload['primary_domain']}`",
            f"- crm_domain: `{payload['crm_domain']}`",
            f"- sector_pack: `{payload['sector_pack']}`",
            f"- website_template: `{payload['website_template']}`",
        ]
    )


def _render_tenant_profile(payload: dict[str, object]) -> dict[str, str]:
    return {
        "tenant_slug": str(payload["tenant_slug"]),
        "tenant_legal_name": str(payload["tenant_legal_name"]),
        "tenant_display_name": str(payload["tenant_display_name"]),
        "crm_platform_name": str(payload["crm_platform_name"]),
        "crm_platform_tagline": str(payload["crm_platform_tagline"]),
        "brand_logo": str(payload["brand_logo"]),
        "brand_logo_alt": str(payload["brand_logo_alt"]),
        "brand_sidebar_subtitle": str(payload["brand_sidebar_subtitle"]),
        "auth_cookie_access": str(payload["auth_cookie_access"]),
        "auth_cookie_refresh": str(payload["auth_cookie_refresh"]),
        "csrf_cookie_name": str(payload["csrf_cookie_name"]),
    }


def _render_operations_commands() -> str:
    return "\n".join(
        [
            "# Operations Commands",
            "",
            "```bash",
            "cd CRM",
            "source .maridav/bin/activate",
            "python manage.py check",
            "python manage.py test -v 1",
            "python manage.py setup_roles",
            "python manage.py run_sla_orchestration",
            "python manage.py run_observability_checks --window-minutes 5",
            "python manage.py setup_enterprise_connectors --activate",
            "python manage.py run_enterprise_connectors",
            "```",
            "",
            "## Media routing guard (local/staging Django run)",
            "Keep these invariants in URL configs:",
            "- `MEDIA_URL=/media/`",
            "- `static(settings.MEDIA_URL, ...)` declared before `path('', include('website.urls'))`.",
            "",
            "Quick route check:",
            "```bash",
            "python manage.py shell -c \"from django.urls import resolve; m = resolve('/media/careers/route-check.pdf'); print(m.func.__module__ + '.' + m.func.__name__)\"",
            "# Expected in DEBUG mode: django.views.static.serve",
            "```",
            "",
            "## Scheduler recommendations",
            "```bash",
            "*/5 * * * * cd <repo-root>/CRM && source .maridav/bin/activate && python manage.py run_sla_orchestration >> /var/log/maridav_sla.log 2>&1",
            "*/5 * * * * cd <repo-root>/CRM && source .maridav/bin/activate && python manage.py run_observability_checks >> /var/log/maridav_observability.log 2>&1",
            "*/2 * * * * cd <repo-root>/CRM && source .maridav/bin/activate && python manage.py run_enterprise_connectors >> /var/log/maridav_enterprise_connectors.log 2>&1",
            "```",
            "",
        ]
    )


class Command(BaseCommand):
    help = "Assemble un client kit WaasPlus PackPlus (docs + env + checklist + templates)."

    def add_arguments(self, parser):
        parser.add_argument("--client-name", default="Client PackPlus", help="Nom client affiché dans le kit.")
        parser.add_argument("--primary-domain", default="example.ci", help="Domaine principal client.")
        parser.add_argument("--crm-domain", default="", help="Domaine CRM (défaut: crm.<primary-domain>).")
        parser.add_argument("--sector-pack", default="services_b2b", choices=sorted(SECTOR_PACKS.keys()))
        parser.add_argument("--website-template", default="template_01", help="Template web à inclure.")
        parser.add_argument("--target-environment", default="prod", choices=["dev", "staging", "prod"])
        parser.add_argument(
            "--output-dir",
            default="",
            help="Dossier de sortie des kits (défaut: <repo>/packplus_client_kits).",
        )
        parser.add_argument("--kit-id", default="", help="Identifiant de kit (sinon auto horodaté).")
        parser.add_argument("--zip", action="store_true", help="Génère aussi une archive zip.")
        parser.add_argument(
            "--export-dir",
            default="",
            help="Dossier optionnel pour copier le kit généré (ex: dossier Waas final).",
        )
        parser.add_argument("--force", action="store_true", help="Ecrase un kit existant du même nom.")

    def handle(self, *args, **options):
        repo_root = Path(__file__).resolve().parents[4]
        markdown_root = repo_root / "markdown"
        templates_root = repo_root / "templates_catalog"

        client_name = str(options["client_name"]).strip() or "Client PackPlus"
        primary_domain = str(options["primary_domain"]).strip().lower()
        crm_domain = str(options["crm_domain"]).strip().lower() or f"crm.{primary_domain}"
        sector_pack = str(options["sector_pack"]).strip()
        website_template = str(options["website_template"]).strip()
        target_environment = str(options["target_environment"]).strip()

        if not primary_domain:
            raise CommandError("--primary-domain est obligatoire.")
        if sector_pack not in SECTOR_PACKS:
            raise CommandError(f"Sector pack inconnu: {sector_pack}")

        output_dir = Path(options["output_dir"]).expanduser() if options.get("output_dir") else (repo_root / "packplus_client_kits")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        kit_id = str(options.get("kit_id") or "").strip() or f"{_slugify(client_name)}_{timestamp}"
        kit_path = output_dir / kit_id

        if kit_path.exists():
            if not options.get("force"):
                raise CommandError(f"Le kit existe déjà: {kit_path}. Utiliser --force pour écraser.")
            shutil.rmtree(kit_path)

        tenant_slug = _slugify(client_name)
        payload: dict[str, object] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "kit_id": kit_id,
            "client_name": client_name,
            "tenant_slug": tenant_slug,
            "tenant_legal_name": client_name,
            "tenant_display_name": client_name,
            "crm_platform_name": f"CRM {client_name}",
            "crm_platform_tagline": "Performance & Excellence operationnelle",
            "brand_logo": "img/logo_primary.png",
            "brand_logo_alt": client_name,
            "brand_sidebar_subtitle": f"CRM {client_name}".upper(),
            "auth_cookie_access": f"{tenant_slug}_access",
            "auth_cookie_refresh": f"{tenant_slug}_refresh",
            "csrf_cookie_name": f"{tenant_slug}_csrf",
            "primary_domain": primary_domain,
            "crm_domain": crm_domain,
            "cookie_domain": f".{primary_domain}",
            "sector_pack": sector_pack,
            "sector_profile": SECTOR_PACKS[sector_pack],
            "website_template": website_template,
            "target_environment": target_environment,
        }

        (kit_path / "docs" / "markdown").mkdir(parents=True, exist_ok=True)
        (kit_path / "templates").mkdir(parents=True, exist_ok=True)

        # Generated operational files.
        generated_files: list[str] = []
        onboarding_file = kit_path / "client_onboarding.yaml"
        onboarding_file.write_text(_render_onboarding_yaml(payload), encoding="utf-8")
        generated_files.append(str(onboarding_file.relative_to(kit_path)))

        env_file = kit_path / "deployment.env.example"
        env_file.write_text(_render_env_example(payload), encoding="utf-8")
        generated_files.append(str(env_file.relative_to(kit_path)))

        checklist_file = kit_path / "delivery_checklist.md"
        checklist_file.write_text(_render_delivery_checklist(payload), encoding="utf-8")
        generated_files.append(str(checklist_file.relative_to(kit_path)))

        commands_file = kit_path / "operations_commands.md"
        commands_file.write_text(_render_operations_commands(), encoding="utf-8")
        generated_files.append(str(commands_file.relative_to(kit_path)))

        sector_file = kit_path / "sector_pack_profile.json"
        sector_file.write_text(json.dumps(SECTOR_PACKS[sector_pack], ensure_ascii=False, indent=2), encoding="utf-8")
        generated_files.append(str(sector_file.relative_to(kit_path)))

        tenant_profile_file = kit_path / "tenant_profile.json"
        tenant_profile_file.write_text(
            json.dumps(_render_tenant_profile(payload), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        generated_files.append(str(tenant_profile_file.relative_to(kit_path)))

        # Copy key root docs.
        copied_files: list[str] = []
        for name in ["README.md", "Waas_PackPlus.md", "phases_industrialisation.md", "current_context.md"]:
            src = repo_root / name
            if src.exists():
                dst = kit_path / "docs" / name
                _safe_copy(src, dst)
                copied_files.append(str(dst.relative_to(kit_path)))

        # Copy markdown manuals/runbooks.
        if markdown_root.exists():
            for src in sorted(markdown_root.glob("*.md")):
                dst = kit_path / "docs" / "markdown" / src.name
                _safe_copy(src, dst)
                copied_files.append(str(dst.relative_to(kit_path)))

        # Copy template catalog readme and selected template.
        catalog_readme = templates_root / "README.md"
        if catalog_readme.exists():
            dst = kit_path / "templates" / "README.md"
            _safe_copy(catalog_readme, dst)
            copied_files.append(str(dst.relative_to(kit_path)))

        selected_template = templates_root / website_template
        if selected_template.exists() and selected_template.is_dir():
            shutil.copytree(selected_template, kit_path / "templates" / website_template)
            for copied in sorted((kit_path / "templates" / website_template).rglob("*")):
                if copied.is_file():
                    copied_files.append(str(copied.relative_to(kit_path)))
        else:
            self.stdout.write(self.style.WARNING(f"Template non trouvé dans templates_catalog: {website_template}"))

        manifest = {
            "kit_id": kit_id,
            "generated_at": payload["generated_at"],
            "client": {
                "name": client_name,
                "primary_domain": primary_domain,
                "crm_domain": crm_domain,
                "cookie_domain": payload["cookie_domain"],
                "target_environment": target_environment,
            },
            "productisation": {
                "sector_pack": sector_pack,
                "website_template": website_template,
            },
            "tenant_profile": _render_tenant_profile(payload),
            "files": {
                "generated": generated_files,
                "copied": copied_files,
                "count": len(generated_files) + len(copied_files),
            },
        }
        manifest_file = kit_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        archive_path = ""
        if options.get("zip"):
            zip_base = output_dir / kit_id
            archive_path = shutil.make_archive(str(zip_base), "zip", root_dir=output_dir, base_dir=kit_id)

        export_dir = str(options.get("export_dir") or "").strip()
        export_path = ""
        if export_dir:
            export_target = Path(export_dir).expanduser()
            export_target.mkdir(parents=True, exist_ok=True)
            final_export = export_target / kit_id
            if final_export.exists():
                if not options.get("force"):
                    raise CommandError(f"Le dossier d'export existe déjà: {final_export}. Utiliser --force pour écraser.")
                shutil.rmtree(final_export)
            shutil.copytree(kit_path, final_export)
            export_path = str(final_export)

        self.stdout.write(
            self.style.SUCCESS(
                f"PackPlus client kit generated (kit_id={kit_id}, files={manifest['files']['count']})."
            )
        )
        self.stdout.write(f"WAASPLUS_CLIENT_KIT_PATH={kit_path}")
        if archive_path:
            self.stdout.write(f"WAASPLUS_CLIENT_KIT_ARCHIVE={archive_path}")
        if export_path:
            self.stdout.write(f"WAASPLUS_CLIENT_KIT_EXPORT_PATH={export_path}")
