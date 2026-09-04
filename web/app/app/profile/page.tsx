export default function ProfilePage() {
  return <>
    <div className="eyebrow">Supplier profile</div>
    <h1 className="h1">Define what is commercially relevant to you.</h1>
    <p className="lede">Relevance is deterministic and profile-based. It prioritises categories and geography; it never changes evidence state or becomes a win probability.</p>
    <div className="formgrid" style={{marginTop:24}}>
      <div className="field"><strong>Domains</strong><span className="small">Water · Rail · Ports · Energy systems · Resilience</span></div>
      <div className="field"><strong>CPV families</strong><span className="small">Customer-selected procurement categories</span></div>
      <div className="field"><strong>Geography</strong><span className="small">Portugal MVP · Italy expansion fixture</span></div>
      <div className="field"><strong>Value range</strong><span className="small">Optional deterministic filtering</span></div>
    </div>
    <div className="notice">Profile persistence/auth wiring is intentionally a shell in this build phase. No contact-person or buyer-person intelligence is part of the product.</div>
  </>;
}
