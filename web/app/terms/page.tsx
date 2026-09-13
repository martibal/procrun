import { PublicPage } from "@/components/public-site";

export default function TermsPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Terms</p>
      <h1 className="public-h1">Terms of use.</h1>
      <p className="lede-large">Effective 13 September 2026. These terms govern the current ProcRun website and demo surfaces. ProcRun is a business-to-business service intended only for organisations and persons acting in a professional or commercial capacity. Paid checkout is disabled.</p>
    </section>
    <section className="public-section legal-copy">
      <h2>Service scope</h2><p>ProcRun provides supplier-side procurement intelligence and structured pre-application readiness information. It is an information product, not a tender portal, bid-writing service, legal opinion, professional eligibility assessment, procurement authority or guarantee of commercial or funding outcome.</p>
      <h2>Evidence and interpretation</h2><p>ProcRun keeps source evidence, observable procurement facts and ProcRun-derived interpretation separate. Derived states and mechanical comparisons must be read together with their source scope, date, provenance and stated limitations.</p>
      <h2>Source wording and reuse</h2><p>Source wording is reproduced only where the applicable public reuse basis permits commercial republication. Where a source is restricted to fact extraction, ProcRun exposes only permitted structured facts, citations and official links. A public URL alone is never treated as permission to republish protected wording.</p>
      <h2>Coverage limitation</h2><p><strong>OPEN means that no procurement match satisfying ProcRun&apos;s frozen exact-evidence rules was found in TED as of the stated date.</strong> It does not establish absence outside TED or under different wording, classification or procurement routes.</p>
      <h2>No eligibility or outcome verdict</h2><p>Readiness outputs do not state ELIGIBLE or INELIGIBLE, do not predict approval and do not replace legal, technical, accounting or other professional verification. Context-dependent requirements remain expressly identified for professional verification.</p>
      <h2>No guaranteed completeness</h2><p>ProcRun does not guarantee a complete bill of materials, discovery of every future purchase, supplier suitability, win probability, award outcome, funding approval or complete procurement coverage outside the stated product boundary. Ambiguous evidence remains unresolved rather than being promoted to a stronger conclusion.</p>
      <h2>Source attribution and independence</h2><p>ProcRun uses independently published public sources under their applicable reuse terms. ProcRun is not endorsed by TED, the European Union, OpenCoesione, Regione Lombardia or any other source publisher. Upstream sources may change or become unavailable; ProcRun is designed to fail closed rather than silently broaden a claim.</p>
      <h2>Commercial service status</h2><p>No paid contract can currently be formed through this build. Before checkout is enabled, ProcRun will publish the actual merchant identity and required business disclosures together with the applicable price/VAT treatment, billing and renewal terms, cancellation rules, output licence and intellectual-property terms, acceptable-use rules, suspension provisions, warranty and liability terms, governing law and venue.</p>
    </section>
  </PublicPage>;
}
