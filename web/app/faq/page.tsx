import Link from "next/link";
import { PublicPage } from "@/components/public-site";

const items = [
  ["What problem does ProcRun solve?", "ProcRun helps suppliers inspect funded infrastructure projects and determine, from approved source evidence, which supported components appear to have entered procurement and which still have no relevant TED procurement match at the stated cutoff."],
  ["What does OPEN mean?", "OPEN means: No relevant procurement found in TED as of the stated date. It is a bounded TED search conclusion, not a claim that procurement does not exist nationally, below threshold, or elsewhere."],
  ["What does CLOSED mean?", "CLOSED means accepted procurement evidence shows that the specific supported component has entered procurement at or before the cutoff under ProcRun's matching rules."],
  ["Why would something be UNRESOLVED?", "Because ambiguity is preserved. Incomplete TED retrieval, insufficient corroboration, review-band evidence or an unclear match cannot safely become OPEN or CLOSED."],
  ["Where does the funded-project data come from?", "The approved funded-project source is the exact OpenCoesione 2021–2027 EU-cohesion operation-list publication family. The current live funded-project route is PR FESR Lombardia."],
  ["Where does procurement evidence come from?", "Tenders Electronic Daily (TED), published by the Publications Office of the European Union, is the approved MVP source for procurement evidence and the bounded negative-search scope."],
  ["Does ProcRun cover every public procurement?", "No. ProcRun explicitly does not claim complete national procurement coverage. National-only and below-threshold procedures may sit outside the TED publication universe."],
  ["Does ProcRun predict which tenders I will win?", "No. ProcRun is not a win-probability model, bid writer or GO/NO-GO engine. Supplier relevance can help order information, but it cannot change the underlying evidence state."],
  ["Does ProcRun contain buyer or contact intelligence?", "No. The intelligence plane excludes natural-person data. Customer account and billing data belong to a separate control plane and are not analytical inputs."],
  ["Can I export the data?", "The planned launch package includes customer-safe CSV export. Exports are constrained to the approved read model and do not expose raw source payloads or internal model data."],
  ["Is the source data endorsed by the EU or Italian government?", "No. ProcRun transforms and classifies public source data. Its derived analysis is not an official source publication or endorsement."],
  ["Is the product live for paid customers yet?", "Not yet. The core intelligence delivery is production-ready, while authentication, billing, legal presentation and final customer-web launch controls are still being implemented."],
] as const;

export default function FAQPage() {
  return <PublicPage>
    <section className="page-hero">
      <div className="eyebrow">FAQ</div>
      <h1 className="h1 public-h1">What a customer should know before relying on ProcRun.</h1>
      <p className="lede lede-large">The short version: evidence is inspectable, absence is bounded, and uncertainty is allowed to remain uncertainty.</p>
    </section>
    <section className="public-section faq-list">
      {items.map(([question, answer]) => <article key={question}><h2>{question}</h2><p>{answer}</p></article>)}
    </section>
    <section className="public-section cta-band">
      <div><div className="eyebrow">Need the formal evidence rules?</div><h2 className="display-h2 compact-heading">Read the methodology and coverage definitions.</h2></div>
      <Link className="button large" href="/methodology">Open methodology</Link>
    </section>
  </PublicPage>;
}
