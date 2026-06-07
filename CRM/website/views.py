import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse


PUBLIC_ROOT = settings.BASE_DIR.parent
TEMPLATES_ROOT = PUBLIC_ROOT / "templates_catalog"
BRIDGE_SCRIPT_TAG = '<script src="assets/js/site-crm-bridge.js"></script>'
DENY_PREFIXES = (
    ".git",
    "CRM",
    "apps",
    "packages",
    "node_modules",
)
ALLOWED_SUFFIXES = {
    ".html",
    ".css",
    ".js",
    ".map",
    ".json",
    ".txt",
    ".xml",
    ".webmanifest",
    ".webm",
    ".mp4",
    ".m4v",
    ".ogv",
    ".avif",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".svg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".pdf",
}


def _resolve_public_path(path: str) -> Path:
    clean = (path or "").strip("/")
    if not clean:
        clean = "index.html"

    preferred_template = (getattr(settings, "WEBSITE_TEMPLATE", "template_01") or "template_01").strip()
    candidates = []
    if preferred_template and preferred_template != "template_01":
        candidates.append(TEMPLATES_ROOT / preferred_template / clean)
    candidates.append(PUBLIC_ROOT / clean)

    for raw_candidate in candidates:
        candidate = raw_candidate.resolve()
        try:
            candidate.relative_to(PUBLIC_ROOT)
        except ValueError:
            continue

        if any(part.startswith(".") for part in candidate.relative_to(PUBLIC_ROOT).parts):
            continue

        if any(str(candidate.relative_to(PUBLIC_ROOT)).startswith(prefix) for prefix in DENY_PREFIXES):
            continue

        if candidate.is_dir():
            candidate = (candidate / "index.html").resolve()

        if not candidate.exists() and "." not in candidate.name:
            html_candidate = candidate.with_suffix(".html")
            if html_candidate.exists():
                candidate = html_candidate

        if not candidate.exists() or not candidate.is_file():
            continue

        if candidate.suffix.lower() not in ALLOWED_SUFFIXES:
            continue

        return candidate

    raise Http404("Not found")


def _inject_bridge_script(html: str) -> str:
    if "site-crm-bridge.js" in html:
        return html
    if "</body>" in html:
        return html.replace("</body>", f"{BRIDGE_SCRIPT_TAG}\n</body>")
    return html + f"\n{BRIDGE_SCRIPT_TAG}\n"


def legacy_site(request, path=""):
    file_path = _resolve_public_path(path)

    content_type, _ = mimetypes.guess_type(file_path.name)
    content_type = content_type or "application/octet-stream"

    if file_path.suffix.lower() == ".html":
        try:
            html = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            html = file_path.read_text(encoding="latin-1")
        html = _inject_bridge_script(html)
        return HttpResponse(html, content_type="text/html; charset=utf-8")

    return FileResponse(file_path.open("rb"), content_type=content_type)
