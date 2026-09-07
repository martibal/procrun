import type { PublicHistoryObservation } from "@/lib/public-history";

export type HistoryChangeKind =
  | "FIRST_OBSERVATION"
  | "STATE_CHANGED"
  | "EVIDENCE_CHANGED"
  | "COVERAGE_CHANGED"
  | "CORRECTION"
  | "HEARTBEAT";

export type HistoryChange = {
  kind: HistoryChangeKind;
  changedFields: readonly string[];
  summary: string;
};

export function describeHistoryChange(
  previous: PublicHistoryObservation | undefined,
  current: PublicHistoryObservation,
): HistoryChange {
  if (!previous) {
    return {
      kind: "FIRST_OBSERVATION",
      changedFields: ["state"],
      summary: `First stored observation: ${current.state}.`,
    };
  }

  const changedFields: string[] = [];
  if (previous.state !== current.state) changedFields.push("state");
  if (previous.evidenceReference !== current.evidenceReference) changedFields.push("evidence_reference");
  if (previous.evidenceUrl !== current.evidenceUrl) changedFields.push("evidence_url");
  if (previous.evidenceExcerpt !== current.evidenceExcerpt) changedFields.push("evidence_excerpt");
  if (previous.coverageNote !== current.coverageNote) changedFields.push("coverage_note");

  if (current.correction) {
    const stateSuffix = previous.state !== current.state
      ? ` State changed from ${previous.state} to ${current.state}.`
      : "";
    return {
      kind: "CORRECTION",
      changedFields,
      summary: `Correction appended to the immutable history.${stateSuffix}`,
    };
  }

  if (previous.state !== current.state) {
    return {
      kind: "STATE_CHANGED",
      changedFields,
      summary: `State changed from ${previous.state} to ${current.state}.`,
    };
  }

  if (changedFields.some((field) => field.startsWith("evidence_"))) {
    return {
      kind: "EVIDENCE_CHANGED",
      changedFields,
      summary: `Procurement evidence changed while state remained ${current.state}.`,
    };
  }

  if (changedFields.includes("coverage_note")) {
    return {
      kind: "COVERAGE_CHANGED",
      changedFields,
      summary: `Coverage wording changed while state remained ${current.state}.`,
    };
  }

  return {
    kind: "HEARTBEAT",
    changedFields: [],
    summary: "No material change; scheduled verification heartbeat.",
  };
}
