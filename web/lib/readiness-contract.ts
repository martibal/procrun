export type ReadinessSourceState =
  | "FRESH"
  | "SOURCE_REFRESH_REQUIRED"
  | "INVALIDATED"
  | "INCOMPLETE";

export type ReadinessHistoricalReference =
  | "UNAVAILABLE"
  | "LIMITED_REFERENCE"
  | "ANALYSIS_AVAILABLE";

export interface ReadinessPreviewResponse {
  analysis_available: boolean;
  source_state: ReadinessSourceState;
  historical_reference: ReadinessHistoricalReference;
  customer_message: string;
}

export interface ReadinessProjectInputs {
  bando_code: string;
  benchmark_snapshot_id: string;
  proposed_project_cost_eur: number | null;
  proposed_funding_eur: number;
  proposed_duration_months: number | null;
}

export type ReadinessAdvisorState = "CONFIRMED" | "NOT_CONFIRMED" | "NOT_APPLICABLE";

export interface ReadinessAdvisorConfirmation {
  requirement_id: string;
  state: ReadinessAdvisorState;
}

export interface CommercialValidationBinding {
  validation_id: string;
  validation_sha256: string;
  source_package_id: string;
  source_package_sha256: string;
  benchmark_snapshot_id: string;
  benchmark_snapshot_sha256: string;
}

/**
 * Design-time contract only. Python remains authoritative for all generated
 * matrix, benchmark and dossier values. Frontend code must render these
 * payloads, never recreate readiness calculations locally.
 */
export interface ReadinessUnlockResponse {
  source_package: Record<string, unknown>;
  commercial_validation_release: CommercialValidationBinding;
  published_requirements_matrix: unknown[];
  historical_dimensioning: Record<string, unknown>;
}

export interface ReadinessDossierResponse {
  dossier_id: string;
  canonical_sha256: string;
  payload: Record<string, unknown>;
}

export interface ReadinessErrorResponse {
  error: string;
}
