import { afterAll, beforeAll, describe, expect, it } from "vitest";
import {
  closeWorkspacePoolForTests,
  deleteWorkspace,
  ensureWorkspaceSchema,
  getProfile,
  listSaved,
  putProfile,
  setSaved,
} from "./workspace-db";

const tenantA = "org_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const tenantB = "org_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";

describe("workspace database", () => {
  beforeAll(async () => {
    if (!process.env.PROCRUN_WORKSPACE_DATABASE_URL) {
      throw new Error("PROCRUN_WORKSPACE_DATABASE_URL is required for workspace integration tests");
    }
    await ensureWorkspaceSchema();
    await deleteWorkspace(tenantA);
    await deleteWorkspace(tenantB);
  });

  afterAll(async () => {
    await deleteWorkspace(tenantA);
    await deleteWorkspace(tenantB);
    await closeWorkspacePoolForTests();
  });

  it("isolates profile and saved state by opaque organisation tenant", async () => {
    const profile = await putProfile(tenantA, {
      domains: ["energy_efficiency"],
      cpvPrefixes: ["093312"],
      nutsPrefixes: ["ITC4"],
      minProjectValueEur: 1_000_000,
    });
    await setSaved(tenantA, "OP-1:cmp-1", true);
    await setSaved(tenantB, "OP-2:cmp-2", true);

    expect(await getProfile(tenantA)).toEqual(profile);
    expect(await getProfile(tenantB)).toBeNull();
    expect(await listSaved(tenantA)).toEqual(["OP-1:cmp-1"]);
    expect(await listSaved(tenantB)).toEqual(["OP-2:cmp-2"]);
  });

  it("deletes one workspace without touching another", async () => {
    await setSaved(tenantA, "OP-1:cmp-1", true);
    await setSaved(tenantB, "OP-2:cmp-2", true);
    await deleteWorkspace(tenantA);
    expect(await listSaved(tenantA)).toEqual([]);
    expect(await listSaved(tenantB)).toEqual(["OP-2:cmp-2"]);
  });
});
