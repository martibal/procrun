import "server-only";

import { Pool } from "pg";

let pool: Pool | undefined;
let poolDatabaseUrl: string | undefined;

export function procrunDb(): Pool | undefined {
  const databaseUrl = process.env.PROCRUN_DATABASE_URL;

  if (!databaseUrl) {
    console.error("procrunDb: PROCRUN_DATABASE_URL is not available to the server runtime");
    return undefined;
  }

  if (!pool || poolDatabaseUrl !== databaseUrl) {
    pool = new Pool({
      connectionString: databaseUrl,
      max: 3,
    });
    poolDatabaseUrl = databaseUrl;
  }

  return pool;
}