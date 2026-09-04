"""Fail-closed collector for the approved OpenCoesione 2021-2027 operation-list route."""

from __future__ import annotations

import csv
import hashlib
import io
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Final

from procrun.domain import FundingProject, TemporalProvenance

OPENCOESIONE_SOURCE_ID: Final = "opencoesione_2021_2027_operations"
OPENCOESIONE_PROGRAM_URL: Final = (
    "https://opencoesione.gov.it/it/opendata/beneficiari/2021-2027/"
    "beneficiari_PR_FESR_LOMBARDIA.zip"
)

# Frozen from the live official PR FESR Lombardia 2021-2027 CSV on 2026-09-04.
# Exact names and exact order are intentional: any subsequent change fails before row admission.
EXPECTED_HEADERS: Final[tuple[str, ...]] = (
    "CodiceProgramma_ProgrammeID",
    "Programma_Programme",
    "CodiceLocaleProgetto_OperationLocalIdentifier",
    "CodiceUnicoProgetto_UniqueProjectCode",
    "TitoloProgetto_OperationName",
    "SintesiProgetto_OperationSummary",
    "DataAggiornamento_LastUpdate",
    "CodiceFiscaleBeneficiario_BeneficiaryTaxCode",
    "NomeBeneficiario_BeneficiaryName",
    "CostoTotale_TotalCost",
    "CostoAmmesso_TotalEligibleExpenditure",
    "Fondo_Fund",
    "Ciclo_Period",
    "CategoriaOperazione_CategoryIntervention",
    "ObiettivoSpecifico_SpecificObjective",
    "DataInizioOperazione_OperationStartDate",
    "DataFineOperazione_OperationEndDate",
    "TassoCofinanziamentoUE_EUCofinancingRate",
    "Paese_Country",
    "CodicePostale_Postcode",
)

SOURCE_ONLY_HEADERS: Final[frozenset[str]] = frozenset(
    {
        "CodiceFiscaleBeneficiario_BeneficiaryTaxCode",
        "NomeBeneficiario_BeneficiaryName",
    }
)
ADMITTED_HEADERS: Final[frozenset[str]] = frozenset(EXPECTED_HEADERS) - SOURCE_ONLY_HEADERS


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


def _whole_euros(value: Decimal | None) -> int | None:
    if value is None:
        return None
    integral = value.to_integral_value()
    if integral != value:
        raise OpenCoesioneRowError(f"funding value is not whole-euro compatible: {value!r}")
    return int(integral)


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
    """Validate the complete schema before returning any admitted operation."""
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
        operation_id = row["CodiceLocaleProgetto_OperationLocalIdentifier"].strip()
        operation_name = row["TitoloProgetto_OperationName"].strip()
        operation_summary = row["SintesiProgetto_OperationSummary"].strip()
        if not operation_id:
            raise OpenCoesioneRowError(
                f"row {row_number} lacks operation id; whole batch rejected"
            )
        if not operation_name and not operation_summary:
            raise OpenCoesioneRowError(
                f"row {row_number} lacks both operation name and summary; whole batch rejected"
            )

        # The official operation list can omit one of title/summary on an otherwise valid row.
        # Keep the canonical model total without inventing text: when exactly one is present,
        # reuse that exact published source text as the deterministic fallback for the missing one.
        if not operation_name:
            operation_name = operation_summary
        if not operation_summary:
            operation_summary = operation_name

        updated_on = _parse_date(
            row["DataAggiornamento_LastUpdate"], field="list_updated_on", required=True
        )
        assert updated_on is not None
        updates.add(updated_on)
        staged.append(
            OpenCoesioneOperation(
                operation_id=operation_id,
                cup=row["CodiceUnicoProgetto_UniqueProjectCode"].strip() or None,
                operation_name=operation_name,
                operation_summary=operation_summary,
                start_date=_parse_date(
                    row["DataInizioOperazione_OperationStartDate"], field="start_date"
                ),
                end_date=_parse_date(
                    row["DataFineOperazione_OperationEndDate"], field="end_date"
                ),
                total_cost_eur=_parse_decimal(row["CostoTotale_TotalCost"], field="total_cost"),
                eligible_expenditure_eur=_parse_decimal(
                    row["CostoAmmesso_TotalEligibleExpenditure"], field="eligible_expenditure"
                ),
                eu_cofinancing_rate=_parse_decimal(
                    row["TassoCofinanziamentoUE_EUCofinancingRate"],
                    field="eu_cofinancing_rate",
                ),
                fund=row["Fondo_Fund"].strip() or None,
                specific_objective=row["ObiettivoSpecifico_SpecificObjective"].strip() or None,
                postcode=row["CodicePostale_Postcode"].strip() or None,
                country=row["Paese_Country"].strip() or None,
                intervention_category=row["CategoriaOperazione_CategoryIntervention"].strip()
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


def to_funding_projects(batch: OpenCoesioneBatch) -> tuple[FundingProject, ...]:
    """Map only admitted non-person fields into the canonical FundingProject contract.

    CUP is the canonical operation code when present because it is the external project identifier
    that may also appear in TED's EU-funds reference fields.  The OpenCoesione local operation ID
    remains available on the source operation and is used as the immutable source-record identity.
    """
    projects: list[FundingProject] = []
    for operation in batch.operations:
        projects.append(
            FundingProject(
                operation_code=operation.cup or operation.operation_id,
                first_seen_at=batch.observed_at,
                temporal_provenance=TemporalProvenance.RESOLVED,
                project_title=operation.operation_name,
                project_start=operation.start_date,
                project_end=operation.end_date,
                approved_funding_eur=_whole_euros(operation.eligible_expenditure_eur),
                executed_funding_eur=None,
                project_scope_text=operation.operation_summary,
                fund=operation.fund,
                programme="PR FESR Lombardia 2021-2027",
                objective=operation.specific_objective,
                theme=operation.intervention_category,
                region="Lombardia",
                municipality=None,
                nuts_code="ITC4",
                source_url=operation.source_url,
            )
        )
    return tuple(projects)
