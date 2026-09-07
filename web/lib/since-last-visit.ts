import "server-only";

import { Pool, type PoolClient } from "pg";

export type SinceLastVisitSummary = {
  accountId: string;
  newMatchesCount: number | null;
  changedSavedIds: string[];
  firstVisit: boolean;
  sameDayRepeat: boolean;
  freshness: { stale: boolean; text: string };
};

const databaseUrl = process.env.PROCRUN_DATABASE_URL;
const accountId = process.env.PROCRUN_DEV_ACCOUNT_ID;
let pool: Pool | undefined;

function db(): Pool | undefined {
  if (!databaseUrl) return undefined;
  pool ??= new Pool({ connectionString: databaseUrl, max: 3 });
  return pool;
}

async function freshness(client: PoolClient): Promise<SinceLastVisitSummary["freshness"]> {
  const latest = await client.query<{ status: string; completed_at: Date }>(`
    SELECT status, completed_at
    FROM procrun.sync_runs
    WHERE job_name = 'ted_daily'
    ORDER BY completed_at DESC
    LIMIT 1
  `);
  const lastSuccess = await client.query<{ completed_at: Date }>(`
    SELECT completed_at
    FROM procrun.sync_runs
    WHERE job_name = 'ted_daily' AND status = 'SUCCESS'
    ORDER BY completed_at DESC
    LIMIT 1
  `);

  if (latest.rowCount) {
    const row = latest.rows[0];
    const status = await client.query<{ fresh: boolean; local_time: string }>(`
      SELECT
        ($1::timestamptz AT TIME ZONE 'Europe/Rome')::date =
          (now() AT TIME ZONE 'Europe/Rome')::date
        AND ($1::timestamptz AT TIME ZONE 'Europe/Rome')::time >= time '09:30' AS fresh,
        to_char($1::timestamptz AT TIME ZONE 'Europe/Rome', 'HH24:MI') AS local_time
    `, [row.completed_at]);
    if (row.status === "SUCCESS" && status.rows[0].fresh) {
      return { stale: false, text: `Data last checked: today, ${status.rows[0].local_time}` };
    }
  }

  if (lastSuccess.rowCount) {
    const formatted = await client.query<{ day: string }>(`
      SELECT to_char($1::timestamptz AT TIME ZONE 'Europe/Rome', 'DD Mon YYYY') AS day
    `, [lastSuccess.rows[0].completed_at]);
    return {
      stale: true,
      text: `Data may be out of date — last successful check: ${formatted.rows[0].day}.`,
    };
  }
  return { stale: true, text: "Data may be out of date — no successful check recorded." };
}

async function snapshotSavedStates(client: PoolClient, id: string): Promise<void> {
  await client.query(`
    UPDATE procrun.saved_opportunities s
    SET state_at_last_summary = (
      SELECT po.state
      FROM procrun.procurement_observations po
      WHERE po.component_id = s.component_id
      ORDER BY po.observed_at DESC, po.inserted_at DESC
      LIMIT 1
    )
    WHERE s.account_id = $1
      AND EXISTS (
        SELECT 1 FROM procrun.procurement_observations po
        WHERE po.component_id = s.component_id
      )
  `, [id]);
}

export async function loadSinceLastVisitSummary(): Promise<SinceLastVisitSummary | null> {
  const activePool = db();
  if (!activePool || !accountId) return null;

  let client: PoolClient | undefined;
  try {
    client = await activePool.connect();
    await client.query("BEGIN");
    const account = await client.query<{ last_active_summary_at: Date | null }>(`
      SELECT last_active_summary_at
      FROM procrun.accounts
      WHERE account_id = $1
      FOR UPDATE
    `, [accountId]);
    if (!account.rowCount) {
      await client.query("ROLLBACK");
      return null;
    }

    const fresh = await freshness(client);
    const previous = account.rows[0].last_active_summary_at;
    if (previous === null) {
      await snapshotSavedStates(client, accountId);
      await client.query(
        "UPDATE procrun.accounts SET last_active_summary_at = now() WHERE account_id = $1",
        [accountId],
      );
      await client.query("COMMIT");
      return {
        accountId,
        newMatchesCount: null,
        changedSavedIds: [],
        firstVisit: true,
        sameDayRepeat: false,
        freshness: fresh,
      };
    }

    const day = await client.query<{ same_day: boolean }>(`
      SELECT
        ($1::timestamptz AT TIME ZONE 'Europe/Rome')::date =
        (now() AT TIME ZONE 'Europe/Rome')::date AS same_day
    `, [previous]);
    if (day.rows[0].same_day) {
      await client.query("COMMIT");
      return {
        accountId,
        newMatchesCount: null,
        changedSavedIds: [],
        firstVisit: false,
        sameDayRepeat: true,
        freshness: fresh,
      };
    }

    const matches = await client.query<{ count: string }>(`
      SELECT count(*)::text AS count
      FROM procrun.component_matches
      WHERE account_id = $1 AND first_matched_at > $2
    `, [accountId, previous]);
    const changed = await client.query<{ component_id: string }>(`
      SELECT DISTINCT s.component_id
      FROM procrun.saved_opportunities s
      JOIN LATERAL (
        SELECT po.state, po.observed_at
        FROM procrun.procurement_observations po
        WHERE po.component_id = s.component_id
          AND po.observed_at::timestamptz > $2
        ORDER BY po.observed_at DESC, po.inserted_at DESC
        LIMIT 1
      ) latest ON true
      WHERE s.account_id = $1
        AND s.state_at_last_summary IS NOT NULL
        AND latest.state <> s.state_at_last_summary
      ORDER BY s.component_id
    `, [accountId, previous]);

    await snapshotSavedStates(client, accountId);
    await client.query(
      "UPDATE procrun.accounts SET last_active_summary_at = now() WHERE account_id = $1",
      [accountId],
    );
    await client.query("COMMIT");
    return {
      accountId,
      newMatchesCount: Number(matches.rows[0].count),
      changedSavedIds: changed.rows.map((row) => row.component_id),
      firstVisit: false,
      sameDayRepeat: false,
      freshness: fresh,
    };
  } catch {
    if (client) {
      try {
        await client.query("ROLLBACK");
      } catch {
        // The optional activity database may already be unavailable.
      }
    }
    return null;
  } finally {
    client?.release();
  }
}
