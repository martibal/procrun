from __future__ import annotations

import httpx

PAGE_URL = "https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/"
ZIP_URL = (
    "https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/"
    "beneficiari_PR_FESR_LOMBARDIA.zip"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,it;q=0.8",
}


def main() -> None:
    with httpx.Client(timeout=30.0, follow_redirects=True, headers=HEADERS) as client:
        page = client.get(PAGE_URL)
        print(f"page_status={page.status_code}")
        print(f"page_final_host={page.url.host}")
        print(f"cookie_names={sorted(cookie.name for cookie in client.cookies.jar)}")
        page.raise_for_status()

        response = client.get(
            ZIP_URL,
            headers={
                "Accept": "application/zip,application/octet-stream;q=0.9,*/*;q=0.8",
                "Referer": PAGE_URL,
            },
        )
        print(f"zip_status={response.status_code}")
        print(f"zip_final_host={response.url.host}")
        print(f"zip_content_type={response.headers.get('content-type', '<missing>')}")
        print(f"zip_bytes={len(response.content)}")
        response.raise_for_status()
        if not response.content.startswith(b"PK"):
            raise SystemExit("response is not a ZIP payload")


if __name__ == "__main__":
    main()
