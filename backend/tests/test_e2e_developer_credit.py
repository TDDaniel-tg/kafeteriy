"""
E2E and Acceptance Tests for Developer Credit Requirement (Section 15 of TZ).
Verifies that DeveloperCredit ("Разработано TDDaniel" -> https://tddaniel.netlify.app)
is present across manifests, documentation, compiled bundle, and rendered in DOM via Playwright.
"""

import os
import json
import socket
import threading
import http.server
from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)
    
    def log_message(self, format, *args):
        pass  # suppress logs

@pytest.fixture(scope="module")
def frontend_server():
    port = get_free_port()
    server = http.server.HTTPServer(('127.0.0.1', port), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{port}"
    yield url
    server.shutdown()

def test_developer_credit_static_manifests():
    """Verify Section 15: Developer credit in package.json, pyproject.toml, and docs."""
    # package.json
    pkg_path = FRONTEND_DIR / "package.json"
    assert pkg_path.exists()
    pkg_data = json.loads(pkg_path.read_text(encoding="utf-8"))
    assert "TDDaniel" in pkg_data.get("author", "")
    assert "https://tddaniel.netlify.app" in pkg_data.get("author", "")

    # pyproject.toml
    pyproject_path = BASE_DIR / "backend" / "pyproject.toml"
    assert pyproject_path.exists()
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    assert "TDDaniel" in pyproject_text
    assert "https://tddaniel.netlify.app" in pyproject_text

    # README.md
    readme_path = BASE_DIR / "README.md"
    assert readme_path.exists()
    readme_text = readme_path.read_text(encoding="utf-8")
    assert "Разработано TDDaniel" in readme_text
    assert "https://tddaniel.netlify.app" in readme_text

    # docs/
    for doc_name in [
        "ADMIN_GUIDE.md",
        "EMPLOYEE_GUIDE.md",
        "INTEGRATIONS.md",
        "UAT_SCENARIOS.md",
        "REQUIREMENTS_COVERAGE.md"
    ]:
        doc_path = BASE_DIR / "docs" / doc_name
        assert doc_path.exists(), f"Missing doc: {doc_name}"
        doc_content = doc_path.read_text(encoding="utf-8")
        assert "TDDaniel" in doc_content, f"Missing TDDaniel attribution in {doc_name}"
        assert "https://tddaniel.netlify.app" in doc_content, f"Missing netlify link in {doc_name}"

def test_developer_credit_in_compiled_bundle():
    """Verify Section 15: Developer credit compiled into production bundle."""
    js_files = list((DIST_DIR / "assets").glob("index-*.js"))
    assert len(js_files) > 0, "No compiled JS bundle found in dist/assets"
    
    found = False
    for js_file in js_files:
        content = js_file.read_text(encoding="utf-8")
        if "https://tddaniel.netlify.app" in content and "Разработано TDDaniel" in content:
            found = True
            break
    assert found, "Developer credit not found in compiled production JS bundle!"

def test_playwright_e2e_developer_credit_rendered(frontend_server):
    """Verify Section 15: Playwright renders DeveloperCredit with valid href, target, and text."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Load Employee Portal main page
        page.goto(frontend_server, wait_until="domcontentloaded")
        page.wait_for_selector('[data-testid="developer-credit"]', timeout=10000)
        
        # Check Developer Credit component presence
        credit_elements = page.locator('[data-testid="developer-credit"]')
        assert credit_elements.count() >= 1, "DeveloperCredit element not found in DOM"
        
        credit_link = credit_elements.first.locator('a')
        assert credit_link.count() >= 1, "DeveloperCredit link (<a>) not found inside container"
        
        text = credit_link.inner_text()
        assert "Разработано TDDaniel" in text, f"Unexpected credit text: {text}"
        
        href = credit_link.get_attribute("href")
        assert href == "https://tddaniel.netlify.app", f"Unexpected credit href: {href}"
        
        target = credit_link.get_attribute("target")
        assert target == "_blank", f"Expected target='_blank', got: {target}"
        
        rel = credit_link.get_attribute("rel")
        assert "noopener" in rel and "noreferrer" in rel, f"Expected rel='noopener noreferrer', got: {rel}"
        
        # 2. Switch to Admin Panel ("Пульт") and verify Developer Credit
        admin_button = page.locator('button:has-text("Пульт"), button:has-text("Админ")')
        if admin_button.count() > 0:
            admin_button.first.click()
            page.wait_for_timeout(500)
            admin_credit = page.locator('[data-testid="developer-credit"]')
            assert admin_credit.count() >= 1, "DeveloperCredit missing in Admin Panel"
            admin_link = admin_credit.first.locator('a')
            assert "Разработано TDDaniel" in admin_link.inner_text()
            assert admin_link.get_attribute("href") == "https://tddaniel.netlify.app"
            
        browser.close()
