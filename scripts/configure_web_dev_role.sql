\set ON_ERROR_STOP on

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'procrun_web_dev'
    ) THEN
        CREATE ROLE procrun_web_dev
            LOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOINHERIT;
    END IF;
END
$$;

GRANT CONNECT ON DATABASE procrun TO procrun_web_dev;
GRANT USAGE ON SCHEMA procrun TO procrun_web_dev;

REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA procrun FROM procrun_web_dev;

GRANT SELECT (
    version_id,
    operation_code,
    as_of,
    project_title,
    project_start,
    project_end,
    approved_funding_eur,
    executed_funding_eur,
    project_scope_text,
    fund,
    programme,
    objective,
    theme,
    region,
    nuts_code,
    inserted_at
) ON procrun.funding_project_versions TO procrun_web_dev;

GRANT SELECT (
    version_id,
    component_id,
    operation_code,
    as_of,
    category,
    description,
    scope_evidence,
    inserted_at
) ON procrun.component_versions TO procrun_web_dev;

GRANT SELECT (
    id,
    component_id,
    operation_code,
    observed_at,
    state,
    evidence_reference,
    evidence_url,
    evidence_excerpt,
    coverage_note,
    correction_of_id,
    inserted_at
) ON procrun.procurement_observations TO procrun_web_dev;

GRANT SELECT (
    job_name,
    status,
    completed_at
) ON procrun.sync_runs TO procrun_web_dev;

GRANT SELECT (
    account_id,
    last_active_summary_at
) ON procrun.accounts TO procrun_web_dev;
GRANT UPDATE (last_active_summary_at)
    ON procrun.accounts TO procrun_web_dev;

GRANT SELECT (
    account_id,
    component_id,
    first_matched_at
) ON procrun.component_matches TO procrun_web_dev;

GRANT SELECT (
    account_id,
    component_id,
    state_at_last_summary
) ON procrun.saved_opportunities TO procrun_web_dev;
GRANT UPDATE (state_at_last_summary)
    ON procrun.saved_opportunities TO procrun_web_dev;

COMMIT;

\echo 'Role grants applied. Set the password separately with: \\password procrun_web_dev'
