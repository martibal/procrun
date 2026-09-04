import Link from "next/link";

export default function HomePage() {
  return <>
    <div className="eyebrow">Infrastructure procurement intelligence</div>
    <h1 className="h1">See the evidence behind what may still be left to buy.</h1>
    <p className="lede">ProcRun turns approved project scope into evidence-backed components and checks procurement evidence against a bounded source universe. The MVP negative-search boundary is TED, and the product says so explicitly.</p>
    <div style={{display:"flex", gap:12, marginTop:24}}><Link className="button" href="/app">Open fixture app</Link><Link className="button" href="/methodology">Read methodology</Link></div>
    <div className="notice"><strong>Current build:</strong> customer-safe fixture environment. No fixture is represented as live production data.</div>
  </>;
}
