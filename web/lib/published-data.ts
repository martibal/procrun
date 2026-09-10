import { readFile } from "node:fs/promises";

export type ProjectState = "OPEN" | "CLOSED" | "PARTIAL" | "UNRESOLVED";
export type ComponentState = "OPEN" | "CLOSED" | "UNRESOLVED";

export type SourceSpan = {
  source_field: string;
  text: string;
  start: number;
  end: number;
};

export type ProcurementMatch = {
  evidence_id: string;
  notice_id: string;
  publication_date: string;
  title: string;
  source_url: string;
  cpv_codes: string[];
  estimated_value_eur: number | null;
  nuts_code: string | null;
  project_reference: string | null;
  evidence: SourceSpan;
};

export type RunwayComponent = {
  component_id: string;
  category: string;
  label: string;
  state: ComponentState;
  cutoff_date: string;
  project_evidence: SourceSpan;
  procurement_matches: ProcurementMatch[];
  coverage_note: string;
  state_explanation: string;
};

export type RunwayProject = {
  operation_code: string;
  project_title: string | null;
  project_start: string | null;
  project_end: string | null;
  approved_funding_eur: number | null;
  programme: string | null;
  region: string | null;
  nuts_code: string | null;
  source_url: string;
  source_evidence: {
    source_type: "Project title" | "Project description";
    source_field: string;
    text: string;
    start: number;
    end: number;
    source_url: string;
  };
  state: ProjectState;
  cutoff_date: string;
  components: RunwayComponent[];
  unresolved_source_evidence: SourceSpan[];
  orchestration_version: string;
  component_rule_version: string;
  match_rule_version: string;
  project_classifier_version: string;
  read_model_version: string;
  content_hash: string;
};

export type Opportunity = {
  id: string;
  projectId: string;
  projectTitle: string;
  componentId: string | null;
  componentCategory: string | null;
  component: string;
  state: ComponentState;
  cutoffDate: string;
  coverage: "TED";
  openWording?: string;
  projectEvidenceType: "Project title" | "Project description";
  projectEvidence: string;
  unresolvedEvidence: string[];
  procurementEvidence?: string;
  valueEur?: number;
  geography: string;
  sourceVersion: string;
  cpvCodes: string[];
};

function object(value: unknown, name: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${name} must be an object`);
  }
  return value as Record<string, unknown>;
}

function text(value: unknown, name: string): string {
  if (typeof value !== "string" || !value) {
    throw new Error(`${name} must be non-empty text`);
  }
  return value;
}

function span(value: unknown, source: string, sourceBaseOffset = 0): SourceSpan {
  const row = object(value, "source span");
  const start = Number(row.start);
  const end = Number(row.end);
  const valueText = text(row.text, "source span text");
  if (
    !Number.isInteger(start) ||
    !Number.isInteger(end) ||
    start < sourceBaseOffset ||
    end <= start
  ) {
    throw new Error("invalid source span offsets");
  }
  const localStart = start - sourceBaseOffset;
  const localEnd = end - sourceBaseOffset;
  if (
    localStart < 0 ||
    localEnd > source.length ||
    source.slice(localStart, localEnd) !== valueText
  ) {
    throw new Error("source span is not verbatim");
  }
  return {
    source_field: text(row.source_field, "source field"),
    text: valueText,
    start,
    end,
  };
}

export function parseRunwayProject(value: unknown): RunwayProject {
  const row = object(value, "runway project");
  const sourceEvidence = object(row.source_evidence, "source evidence");
  const sourceText = text(sourceEvidence.text, "source evidence text");
  const sourceStart = Number(sourceEvidence.start);
  const sourceEnd = Number(sourceEvidence.end);
  if (
    !Number.isInteger(sourceStart) ||
    !Number.isInteger(sourceEnd) ||
    sourceStart < 0 ||
    sourceEnd <= sourceStart ||
    sourceEnd - sourceStart !== sourceText.length
  ) {
    throw new Error("invalid project source evidence offsets");
  }

  const componentsRaw = Array.isArray(row.components) ? row.components : null;
  if (!componentsRaw) throw new Error("components must be an array");
  const components = componentsRaw.map((item) => {
    const component = object(item, "component");
    const projectEvidence = span(
      component.project_evidence,
      sourceText,
      sourceStart,
    );
    const matchesRaw = Array.isArray(component.procurement_matches)
      ? component.procurement_matches
      : null;
    if (!matchesRaw) throw new Error("procurement_matches must be an array");
    const matches = matchesRaw.map((matchValue) => {
      const match = object(matchValue, "procurement match");
      const evidence = object(match.evidence, "evidence");
      const evidenceText = text(evidence.text, "procurement evidence text");
      const evidenceStart = Number(evidence.start);
      const evidenceEnd = Number(evidence.end);
      if (
        !Number.isInteger(evidenceStart) ||
        !Number.isInteger(evidenceEnd) ||
        evidenceStart < 0 ||
        evidenceEnd <= evidenceStart
      ) {
        throw new Error("invalid procurement evidence offsets");
      }
      return {
        evidence_id: text(match.evidence_id, "evidence id"),
        notice_id: text(match.notice_id, "notice id"),
        publication_date: text(match.publication_date, "publication date"),
        title: text(match.title, "procurement title"),
        source_url: text(match.source_url, "procurement source url"),
        cpv_codes: Array.isArray(match.cpv_codes)
          ? match.cpv_codes.map(String)
          : [],
        estimated_value_eur:
          match.estimated_value_eur == null
            ? null
            : Number(match.estimated_value_eur),
        nuts_code: match.nuts_code == null ? null : String(match.nuts_code),
        project_reference:
          match.project_reference == null
            ? null
            : String(match.project_reference),
        evidence: {
          source_field: text(evidence.source_field, "procurement evidence field"),
          text: evidenceText,
          start: evidenceStart,
          end: evidenceEnd,
        },
      } satisfies ProcurementMatch;
    });
    const state = text(component.state, "component state") as ComponentState;
    if (!["OPEN", "CLOSED", "UNRESOLVED"].includes(state)) {
      throw new Error("invalid component state");
    }
    return {
      component_id: text(component.component_id, "component id"),
      category: text(component.category, "component category"),
      label: text(component.label, "component label"),
      state,
      cutoff_date: text(component.cutoff_date, "cutoff"),
      project_evidence: projectEvidence,
      procurement_matches: matches,
      coverage_note: text(component.coverage_note, "coverage note"),
      state_explanation: text(component.state_explanation, "state explanation"),
    } satisfies RunwayComponent;
  });

  const state = text(row.state, "project state") as ProjectState;
  if (!["OPEN", "CLOSED", "PARTIAL", "UNRESOLVED"].includes(state)) {
    throw new Error("invalid project state");
  }
  const unresolvedRaw = Array.isArray(row.unresolved_source_evidence)
    ? row.unresolved_source_evidence
    : [];
  const unresolved = unresolvedRaw.map((item) =>
    span(item, sourceText, sourceStart),
  );

  const sourceType = text(sourceEvidence.source_type, "source type");
  if (sourceType !== "Project title" && sourceType !== "Project description") {
    throw new Error("invalid project source evidence type");
  }

  return {
    operation_code: text(row.operation_code, "operation code"),
    project_title: row.project_title == null ? null : String(row.project_title),
    project_start: row.project_start == null ? null : String(row.project_start),
    project_end: row.project_end == null ? null : String(row.project_end),
    approved_funding_eur:
      row.approved_funding_eur == null
        ? null
        : Number(row.approved_funding_eur),
    programme: row.programme == null ? null : String(row.programme),
    region: row.region == null ? null : String(row.region),
    nuts_code: row.nuts_code == null ? null : String(row.nuts_code),
    source_url: text(row.source_url, "source url"),
    source_evidence: {
      source_type: sourceType,
      source_field: text(sourceEvidence.source_field, "source field"),
      text: sourceText,
      start: sourceStart,
      end: sourceEnd,
      source_url: text(sourceEvidence.source_url, "source evidence url"),
    },
    state,
    cutoff_date: text(row.cutoff_date, "cutoff date"),
    components,
    unresolved_source_evidence: unresolved,
    orchestration_version: text(
      row.orchestration_version,
      "orchestration version",
    ),
    component_rule_version: text(
      row.component_rule_version,
      "component rule version",
    ),
    match_rule_version: text(row.match_rule_version, "match rule version"),
    project_classifier_version: text(
      row.project_classifier_version,
      "classifier version",
    ),
    read_model_version: text(row.read_model_version, "read model version"),
    content_hash: text(row.content_hash, "content hash"),
  };
}

export async function loadPublishedProjects(): Promise<RunwayProject[]> {
  const path = process.env.PROCRUN_PUBLISHED_JSONL_PATH;
  if (!path) {
    throw new Error("PROCRUN_PUBLISHED_JSONL_PATH is not configured");
  }
  const body = await readFile(path, "utf8");
  const lines = body.split(/\r?\n/).filter((line) => line.trim());
  if (!lines.length) throw new Error("published runway file is empty");
  return lines.map((line) => parseRunwayProject(JSON.parse(line) as unknown));
}

export function toOpportunities(
  projects: readonly RunwayProject[],
): Opportunity[] {
  return projects.flatMap<Opportunity>((project): Opportunity[] => {
    const base = {
      projectId: project.operation_code,
      projectTitle: project.project_title ?? project.source_evidence.text,
      cutoffDate: project.cutoff_date,
      coverage: "TED" as const,
      projectEvidenceType: project.source_evidence.source_type,
      projectEvidence: project.source_evidence.text,
      unresolvedEvidence: project.unresolved_source_evidence.map(
        (item) => item.text,
      ),
      valueEur: project.approved_funding_eur ?? undefined,
      geography:
        [project.region, project.nuts_code].filter(Boolean).join(" · ") ||
        "Not stated",
      sourceVersion: `${project.read_model_version}:${project.content_hash}`,
    };

    if (!project.components.length) {
      const unresolved: Opportunity = {
        ...base,
        id: `${project.operation_code}:unresolved`,
        componentId: null,
        componentCategory: null,
        component: "Source wording requires resolution",
        state: "UNRESOLVED",
        cpvCodes: [],
      };
      return [unresolved];
    }

    return project.components.map((component): Opportunity => ({
      ...base,
      id: `${project.operation_code}:${component.component_id}`,
      componentId: component.component_id,
      componentCategory: component.category,
      component: component.label,
      state: component.state,
      openWording:
        component.state === "OPEN" ? component.state_explanation : undefined,
      procurementEvidence: component.procurement_matches[0]?.evidence.text,
      cpvCodes: [
        ...new Set(
          component.procurement_matches.flatMap((match) => match.cpv_codes),
        ),
      ],
    }));
  });
}

export function toCsv(items: readonly Opportunity[]): string {
  const header = [
    "id",
    "project_title",
    "component",
    "state",
    "cutoff_date",
    "coverage",
    "coverage_wording",
    "project_evidence_type",
    "project_evidence",
    "unresolved_source_evidence",
    "geography",
    "source_version",
  ];
  const quote = (value: string | number | undefined) =>
    `"${String(value ?? "").replaceAll('"', '""')}"`;
  return [
    header.join(","),
    ...items.map((item) =>
      [
        item.id,
        item.projectTitle,
        item.component,
        item.state,
        item.cutoffDate,
        item.coverage,
        item.openWording ?? "",
        item.projectEvidenceType,
        item.projectEvidence,
        item.unresolvedEvidence.join(" | "),
        item.geography,
        item.sourceVersion,
      ]
        .map(quote)
        .join(","),
    ),
  ].join("\n");
}
