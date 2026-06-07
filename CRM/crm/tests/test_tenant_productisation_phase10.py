from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from crm.context_processors import crm_tenant_branding
from crm.services.tenant import resolve_tenant_branding


class TenantBrandingPhase10Tests(SimpleTestCase):
    @override_settings(
        CRM_TENANT_SLUG="acme-ci",
        CRM_TENANT_LEGAL_NAME="ACME Cote d Ivoire",
        CRM_TENANT_DISPLAY_NAME="ACME CI",
        CRM_PLATFORM_NAME="CRM ACME CI",
        CRM_PLATFORM_TAGLINE="Operations et Conformite",
        CRM_BRAND_LOGO="img/acme-logo.png",
        CRM_BRAND_LOGO_ALT="ACME CI",
        CRM_BRAND_SIDEBAR_SUBTITLE="CRM ACME",
    )
    def test_resolve_tenant_branding_uses_runtime_settings(self):
        branding = resolve_tenant_branding()

        self.assertEqual(branding["tenant_slug"], "acme-ci")
        self.assertEqual(branding["legal_name"], "ACME Cote d Ivoire")
        self.assertEqual(branding["display_name"], "ACME CI")
        self.assertEqual(branding["crm_name"], "CRM ACME CI")
        self.assertEqual(branding["tagline"], "Operations et Conformite")
        self.assertEqual(branding["logo_path"], "img/acme-logo.png")
        self.assertEqual(branding["logo_alt"], "ACME CI")
        self.assertEqual(branding["sidebar_subtitle"], "CRM ACME")
        self.assertTrue(branding["logo_url"].endswith("/static/img/acme-logo.png"))

    @override_settings(
        CRM_TENANT_DISPLAY_NAME="Tenant Test",
        CRM_PLATFORM_NAME="CRM Tenant Test",
    )
    def test_context_processor_exposes_crm_branding(self):
        request = RequestFactory().get("/crm/")
        context = crm_tenant_branding(request)

        self.assertIn("crm_branding", context)
        self.assertEqual(context["crm_branding"]["display_name"], "Tenant Test")
        self.assertEqual(context["crm_branding"]["crm_name"], "CRM Tenant Test")


class TenantPackPlusPhase10Tests(TestCase):
    def test_build_packplus_client_kit_generates_tenant_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout = StringIO()
            call_command(
                "build_packplus_client_kit",
                "--client-name",
                "Aster CI",
                "--primary-domain",
                "aster.ci",
                "--sector-pack",
                "services_b2b",
                "--website-template",
                "template_01",
                "--output-dir",
                tmpdir,
                "--kit-id",
                "aster-kit",
                stdout=stdout,
            )
            kit_path = Path(tmpdir) / "aster-kit"

            tenant_profile = json.loads((kit_path / "tenant_profile.json").read_text(encoding="utf-8"))
            self.assertEqual(tenant_profile["tenant_slug"], "aster-ci")
            self.assertEqual(tenant_profile["tenant_display_name"], "Aster CI")
            self.assertEqual(tenant_profile["auth_cookie_access"], "aster-ci_access")

            env_text = (kit_path / "deployment.env.example").read_text(encoding="utf-8")
            self.assertIn("CRM_TENANT_SLUG=aster-ci", env_text)
            self.assertIn("CRM_TENANT_DISPLAY_NAME=Aster CI", env_text)
            self.assertIn("AUTH_COOKIE_ACCESS=aster-ci_access", env_text)

            manifest = json.loads((kit_path / "manifest.json").read_text(encoding="utf-8"))
            self.assertIn("tenant_profile", manifest)
            self.assertEqual(manifest["tenant_profile"]["tenant_slug"], "aster-ci")
