from __future__ import annotations

import httpx

PAGE_URL = "https://opencoesione.gov.it/it/beneficiari_operazioni_2021_2027/"
ZIP_URL = (
    "https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/"
    "beneficiari_PR_FESR_LOMBARDIA.zip"
)


def main() -> None:
    headers = {"User-Agent": "ProcRun/0.1 public-open-data-transport-check"}
    with httpx.Client(timeout=30.0, follow_redirects=True, headers=headers) as client:
        page = client.get(PAGE_URL)
        print(f"page_status={page.status_code}")
        print(f"page_type={page.headers.get('content-type', '<missing>')}")
        response = client.get(ZIP_URL)
        print(f"zip_status={response.status_code}")
        print(f"zip_type={response.headers.get('content-type', '<missing>')}")
        print(f"zip_bytes={len(response.content)}")
        if response.status_code == 200:
            if not response.content.startswith(b"PK"):
                raise SystemExit("200 response is not ZIP")
        else:
            raise SystemExit(f"transport blocked with HTTP {response.status_code}")


if __name__ == "__main__":
    main()
