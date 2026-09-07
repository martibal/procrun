import "server-only";

import { Pool } from "pg";

const databaseUrl = process.env.PROCRUN_DATABASE_URL;
let pool: Pool | undefined;

export function procrunDb(): Pool | undefined {
  if (!databaseUrl) return undefined;
  pool ??= new Pool({ connectionString: databaseUrl, max: 3 });
  return pool;
}