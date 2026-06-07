from __future__ import annotations

import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase


class PackPlusProductisationPhase6Tests(TestCase):
    def test_build_packplus_client_kit_generates_manifest_and_variables(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout = StringIO()
            call_command(
                "build_packplus_client_kit",
                "--client-name",
                "ACME CI",
                "--primary-domain",
                "acme.ci",
                "--sector-pack",
                "services_b2b",
                "--website-template",
                "template_01",
                "--output-dir",
                tmpdir,
                "--kit-id",
                "acme-kit",
                stdout=stdout,
            )
            output = stdout.getvalue()
            kit_path = Path(tmpdir) / "acme-kit"

            self.assertIn("WAASPLUS_CLIENT_KIT_PATH=", output)
            self.assertTrue(kit_path.exists())
            self.assertTrue((kit_path / "manifest.json").exists())
            self.assertTrue((kit_path / "client_onboarding.yaml").exists())
            self.assertTrue((kit_path / "deployment.env.example").exists())
            self.assertTrue((kit_path / "tenant_profile.json").exists())
            self.assertTrue((kit_path / "docs" / "README.md").exists())
            self.assertTrue((kit_path / "docs" / "current_context.md").exists())

            manifest = json.loads((kit_path / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["kit_id"], "acme-kit")
            self.assertEqual(manifest["client"]["primary_domain"], "acme.ci")
            self.assertEqual(manifest["productisation"]["sector_pack"], "services_b2b")
            self.assertEqual(manifest["productisation"]["website_template"], "template_01")
            self.assertEqual(manifest["tenant_profile"]["tenant_slug"], "acme-ci")

            operations_doc = (kit_path / "operations_commands.md").read_text(encoding="utf-8")
            checklist_doc = (kit_path / "delivery_checklist.md").read_text(encoding="utf-8")
            self.assertIn("Media routing guard", operations_doc)
            self.assertIn("resolve('/media/careers/route-check.pdf')", operations_doc)
            self.assertIn("Media file access validated", checklist_doc)

    def test_build_packplus_client_kit_can_zip_and_export(self):
        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as exportdir:
            stdout = StringIO()
            call_command(
                "build_packplus_client_kit",
                "--client-name",
                "Maridav Pack",
                "--primary-domain",
                "maridav.ci",
                "--sector-pack",
                "fmcg_multi_species",
                "--website-template",
                "template_01",
                "--output-dir",
                tmpdir,
                "--export-dir",
                exportdir,
                "--kit-id",
                "maridav-kit",
                "--zip",
                stdout=stdout,
            )
            output = stdout.getvalue()
            kit_path = Path(tmpdir) / "maridav-kit"
            zip_path = Path(tmpdir) / "maridav-kit.zip"
            export_path = Path(exportdir) / "maridav-kit"

            self.assertTrue(kit_path.exists())
            self.assertTrue(zip_path.exists())
            self.assertTrue(export_path.exists())
            self.assertIn("WAASPLUS_CLIENT_KIT_ARCHIVE=", output)
            self.assertIn("WAASPLUS_CLIENT_KIT_EXPORT_PATH=", output)
