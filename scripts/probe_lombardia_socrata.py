from __future__ import annotations

import json

import httpx

DATASET_ID = "q78n-g3m9"
BASE = "https://hub.dati.lombardia.it"
META_URL = f"{BASE}/api/views/{DATASET_ID}"
RESOURCE_URL = f"{BASE}/resource/{DATASET_ID}.json"


def main() -> None:
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        meta = client.get(META_URL)
        print(f"metadata_status={meta.status_code}")
        meta.raise_for_status()
        payload = meta.json()
        columns = payload.get("columns", [])
        fields = [
            {
                "name": column.get("name"),
                "fieldName": column.get("fieldName"),
                "dataTypeName": column.get("dataTypeName"),
                "description": column.get("description"),
            }
            for column in columns
        ]
        print("fields=" + json.dumps(fields, ensure_ascii=True, separators=(",", ":")))

        safe_candidates = [
            field["fieldName"]
            for field in fields
            if field["fieldName"]
            and field["fieldName"]
            not in {"nome_del_beneficiario", "codice_del_beneficiario"}
        ]
        query = {"$select": ",".join(safe_candidates), "$limit": "1"}
        row = client.get(RESOURCE_URL, params=query)
        print(f"projection_status={row.status_code}")
        print(f"projection_url={row.request.url}")
        row.raise_for_status()
        data = row.json()
        if not isinstance(data, list) or not data:
            raise SystemExit("projected endpoint returned no row")
        returned_keys = sorted(data[0].keys())
        print("returned_keys=" + json.dumps(returned_keys, separators=(",", ":")))
        forbidden = {"nome_del_beneficiario", "codice_del_beneficiario"}
        if forbidden & set(returned_keys):
            raise SystemExit("beneficiary identity leaked through projected transport")


if __name__ == "__main__":
    main()
