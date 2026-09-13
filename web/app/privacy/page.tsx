import { PublicPage } from "@/components/public-site";

export default function PrivacyPage() {
  return <PublicPage>
    <section className="page-hero narrow-copy">
      <p className="small">Privacy</p>
      <h1 className="public-h1">Privacy notice.</h1>
      <p className="lede-large">Effective 13 September 2026. This notice describes the current ProcRun data boundary. Paid customer-account and billing integrations are not active and checkout remains disabled until the customer control plane and its full privacy disclosures are configured.</p>
    </section>
    <section className="public-section legal-copy">
      <h2>Intelligence plane</h2><p>ProcRun&apos;s intelligence plane is designed to exclude natural-person identity and contact data. Only sources with an approved, publicly documented data-safety contract may enter this plane. Approved projected sources are validated against frozen field allowlists before normalization, persistence or analytical use.</p>
      <h2>OpenCoesione boundary</h2><p>The approved OpenCoesione 2021–2027 operation-list publication publicly specifies its beneficiary-name field as covering legal persons. Beneficiary name and beneficiary tax identifier are nevertheless treated as source-only identity fields: ProcRun does not admit them into FundingProject, the customer read model, browser/API responses or exports. If that official publication contract changes, the source approval must be reviewed before further production use.</p>
      <h2>Information excluded from customer intelligence</h2><p>Raw source response envelopes, beneficiary identity fields, buyer/contact identity, contact-person details, model prompts and unvalidated candidate text are outside the browser and export contract. ProcRun does not approve a source where privacy safety depends on receiving a broad natural-person identity surface and filtering it afterwards.</p>
      <h2>Customer control plane</h2><p>Future authentication, account, security, subscription, billing, invoicing and support data belong to a separate customer control plane and are never analytical inputs. Before that processing is enabled, this notice will identify the controller, purposes and legal bases, processors and recipients, retention periods, any relevant international-transfer safeguards, data-subject rights and the applicable complaint route.</p>
      <h2>Cookies and tracking</h2><p>The default launch posture is strictly necessary cookies only. Optional analytics, advertising or behavioural tracking must not be enabled without a separate consent and privacy review. No such optional tracking is represented here as active.</p>
      <h2>Current website state</h2><p>This build does not accept payment. Merchant identity, customer-data processors, retention schedules and the customer contact route must be configured and published before commercial checkout is enabled.</p>
    </section>
  </PublicPage>;
}
