from playwright.sync_api import sync_playwright


def main() -> None:
    print("Hello from document-ingestion!")


def fetch_article(url: str, timeout: float = 60 * 1000) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(url, timeout=timeout)
            page.wait_for_load_state("networkidle", timeout=timeout)
            return page.content()
        finally:
            browser.close()
