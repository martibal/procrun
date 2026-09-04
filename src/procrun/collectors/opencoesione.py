"""Fail-closed collector for an approved OpenCoesione 2021-2027 programme operation list.

The current live-transfer pilot is the publicly linked PR FESR Lombardia ZIP/CSV. The
all-program ZIP is deliberately not used because clean CI retrieval returned HTTP 403.
"""

from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Final

import httpx

from procrun.source_contracts import require_live_source

OPENCOESIONE_SOURCE_ID: Final = "opencoesione_2021_2027_operations"
OPENCOESIONE_PROGRAM_URL: Final = (
    "https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/"
    "beneficiari_PR_FESR_LOMBARDIA.zip"
)

EXPECTED_HEADERS: Final[tuple[str, ...]] = (
    "Fondo/Fund",
    "Obiettivo Specifico/Specific Objective",
    "Codice locale progetto/Local identifier of operation",
    "Codice Unico Progetto/Unique project code",
    "Codice fiscale Beneficiario/Beneficiary fiscal code",
    "Nome Beneficiario/Beneficiary name",
    "Denominazione operazione/Operation name",
    "Sintesi operazione/Operation summary",
    "Data inizio operazione/Operation start date",
    "Data fine operazione/Operation end date",
    "Costo Totale/Total cost",
    "Spesa ammissibile/Eligible expenditure",
    "Tasso di cofinanziamento UE/EU co-financing rate",
    "CAP/Postcode",
    "Paese/Country",
    "Categoria di operazione/Category of intervention",
    "Data aggiornamento elenco operazioni/Date of last update of the list of operations",
)

SOURCE_ONLY_HEADERS: Final[frozenset[str]] = frozenset(
    {
        "Codice fiscale Beneficiario/Beneficiary fiscal code",
        "Nome Beneficiario/Beneficiary name",
    }
)


class OpenCoesioneSchemaError(RuntimeError):
    """Raised before admission when route/schema/content is outside the frozen contract."""


class OpenCoesioneRowError(RuntimeError):
    """Raised when any row cannot be mapped safely; the whole batch is discarded."""


@dataclass(frozen=True)
class OpenCoesioneOperation:
    operation_id: str
    cup: str | None
    operation_name: str
    operation_summary: str
    start_date: date | None
    end_date: date | None
    total_cost_eur: Decimal | None
    eligible_expenditure_eur: Decimal | None
    eu_cofinancing_rate: Decimal | None
    fund: str | None
    specific_objective: str | None
    postcode: str | None
    country: str | None
    intervention_category: str | None
    list_updated_on: date
    source_url: str


@dataclass(frozen=True)
class OpenCoesioneBatch:
    operations: tuple[OpenCoesioneOperation, ...]
    observed_at: datetime
    source_url: str
    source_sha256: str
    list_updated_on: date


def _parse_date(value: str, *, field: str, required: bool = False) -> date | None:
    value = value.strip()
    if not value:
        if required:
            raise OpenCoesioneRowError(f"missing required date: {field}")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise OpenCoesioneRowError(f"invalid ISO date in {field}: {value!r}") from exc


def _parse_decimal(value: str, *, field: str) -> Decimal | None:
    value = value.strip().replace(" ", "")
    if not value:
        return None
    if value.count(",") == 1 and "." not in value:
        value = value.replace(",", ".")
    if value.count(",") or value.count(".") > 1:
        raise OpenCoesioneRowError(f"ambiguous numeric value in {field}: {value!r}")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise OpenCoesioneRowError(f"invalid numeric value in {field}: {value!r}") from exc
    if parsed < 0:
        raise OpenCoesioneRowError(f"negative value in {field}: {value!r}")
    return parsed


def _extract_single_csv(payload: bytes) -> bytes:
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
            if len(members) != 1:
                raise OpenCoesioneSchemaError(
                    f"expected exactly one CSV in approved ZIP, found {len(members)}"
                )
            return archive.read(members[0])
    except zipfile.BadZipFile as exc:
        raise OpenCoesioneSchemaError("approved route did not return a valid ZIP archive") from exc


def parse_operation_list_zip(payload: bytes, *, source_url: str) -> OpenCoesioneBatch:
    try:
        csv_text = _extract_single_csv(payload).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise OpenCoesioneSchemaError("operation-list CSV is not UTF-8") from exc

    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")
    if reader.fieldnames is None:
        raise OpenCoesioneSchemaError("operation-list CSV has no header row")
    actual_headers = tuple(header.strip() for header in reader.fieldnames)
    if actual_headers != EXPECTED_HEADERS:
        missing = [header for header in EXPECTED_HEADERS if header not in actual_headers]
        unexpected = [header for header in actual_headers if header not in EXPECTED_HEADERS]
        raise OpenCoesioneSchemaError(
            "OpenCoesione schema drift detected before row admission; "
            f"missing={missing!r}, unexpected={unexpected!r}, order_changed="
            f"{not missing and not unexpected and actual_headers != EXPECTED_HEADERS}"
        )

    staged: list[OpenCoesioneOperation] = []
    updates: set[date] = set()
    for row_number, row in enumerate(reader, start=2):
        if None in row or set(row) != set(EXPECTED_HEADERS):
            raise OpenCoesioneSchemaError(f"row {row_number} violates frozen schema")
        operation_id = row["Codice locale progetto/Local identifier of operation"].strip()
        operation_name = row["Denominazione operazione/Operation name"].strip()
        operation_summary = row["Sintesi operazione/Operation summary"].strip()
        if not operation_id or not operation_name or not operation_summary:
            raise OpenCoesioneRowError(
                f"row {row_number} lacks operation id/name/summary; whole batch rejected"
            )
        updated_on = _parse_date(
            row[
                "Data aggiornamento elenco operazioni/Date of last update of the list of operations"
            ],
            field="list_updated_on",
            required=True,
        )
        assert updated_on is not None
        updates.add(updated_on)
        staged.append(
            OpenCoesioneOperation(
                operation_id=operation_id,
                cup=row["Codice Unico Progetto/Unique project code"].strip() or None,
                operation_name=operation_name,
                operation_summary=operation_summary,
                start_date=_parse_date(
                    row["Data inizio operazione/Operation start date"], field="start_date"
                ),
                end_date=_parse_date(
                    row["Data fine operazione/Operation end date"], field="end_date"
                ),
                total_cost_eur=_parse_decimal(row["Costo Totale/Total cost"], field="total_cost"),
                eligible_expenditure_eur=_parse_decimal(
                    row["Spesa ammissibile/Eligible expenditure"], field="eligible_expenditure"
                ),
                eu_cofinancing_rate=_parse_decimal(
                    row["Tasso di cofinanziamento UE/EU co-financing rate"],
                    field="eu_cofinancing_rate",
                ),
                fund=row["Fondo/Fund"].strip() or None,
                specific_objective=row["Obiettivo Specifico/Specific Objective"].strip() or None,
                postcode=row["CAP/Postcode"].strip() or None,
                country=row["Paese/Country"].strip() or None,
                intervention_category=row[
                    "Categoria di operazione/Category of intervention"
                ].strip()
                or None,
                list_updated_on=updated_on,
                source_url=source_url,
            )
        )

    if not staged:
        raise OpenCoesioneRowError("operation-list CSV contains no data rows")
    if len(updates) != 1:
        raise OpenCoesioneRowError("programme list update date is not uniform across the batch")
    return OpenCoesioneBatch(
        operations=tuple(staged),
        observed_at=datetime.now(timezone.utc),
        source_url=source_url,
        source_sha256=hashlib.sha256(payload).hexdigest(),
        list_updated_on=next(iter(updates)),
    )


def collect_open_coesione(
    *, client: httpx.Client | None = None, timeout_seconds: float = 60.0
) -> OpenCoesioneBatch:
    """Fetch the frozen PR FESR Lombardia pilot route and fail closed on drift."""
    contract = require_live_source(OPENCOESIONE_SOURCE_ID)
    if OPENCOESIONE_PROGRAM_URL not in contract.retrieval_route:
        raise OpenCoesioneSchemaError("runtime source contract does not pin the pilot route")
    owns_client = client is None
    active_client = client or httpx.Client(
        timeout=timeout_seconds,
        follow_redirects=True,
        headers={"User-Agent": "ProcRun/0.1 (public-open-data-ingest)"},
    )
    try:
        response = active_client.get(OPENCOESIONE_PROGRAM_URL)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        if not any(token in content_type for token in ("zip", "octet-stream")):
            raise OpenCoesioneSchemaError(
                f"unexpected content type for approved ZIP route: {content_type or '<missing>'}"
            )
        return parse_operation_list_zip(response.content, source_url=str(response.url))
    finally:
        if owns_client:
            active_client.close()
