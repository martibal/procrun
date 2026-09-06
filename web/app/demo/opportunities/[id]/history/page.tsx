import { notFound } from "next/navigation";
import { PublicPage } from "@/components/public-site";
import { HISTORY_FOOTNOTE } from "@/lib/public-copy";
import { getPublicOpportunityHistory } from "@/lib/public-history";
import { getPublicShowcaseOpportunity } from "@/lib/public-showcase";
import styles from "./history.module.css";

function stateClass(state: "OPEN" | "CLOSED" | "UNRESOLVED"): string {
  if (state === "CLOSED") return styles.closed;
  if (state === "OPEN") return styles.open;
  return styles.unresolved;
}

export default async function PublicOpportunityHistoryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const opportunity = getPublicShowcaseOpportunity(id);
  const history = getPublicOpportunityHistory(id);
  if (!opportunity || history === undefined) notFound();

  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Verifiable history</p>
      <h1 className="h1 public-h1">{opportunity.component}</h1>
      <p className="lede">{opportunity.projectTitle}</p>
      {history.some((item) => item.fixture) ? <div className="notice scope"><strong>Development fixture.</strong> This localhost timeline is synthetic test history used to verify rendering and append-only behaviour. It is not a historical claim about this project.</div> : null}
    </section>

    <section className={`public-section ${styles.timeline}`}>
      {history.length === 0 ? <p>No stored public history is available for this showcase opportunity yet.</p> : history.map((observation) => (
        <article className={styles.entry} key={`${observation.observedAt}-${observation.state}`}>
          <div className={styles.marker} aria-hidden="true" />
          <div>
            <div className={styles.date}>{observation.observedAt}</div>
            <div className={`${styles.state} ${stateClass(observation.state)}`}>{observation.state}</div>
            {observation.state === "CLOSED" ? <>
              <blockquote className={styles.excerpt}>{observation.evidenceExcerpt}</blockquote>
              <a className="text-link strong" href={observation.evidenceUrl} target="_blank" rel="noreferrer">Open TED notice {observation.evidenceReference}</a>
            </> : null}
            <p className="small">{observation.coverageNote}</p>
          </div>
        </article>
      ))}
    </section>

    <section className="public-section legal-copy">
      <p>{HISTORY_FOOTNOTE}</p>
    </section>
  </PublicPage>;
}
