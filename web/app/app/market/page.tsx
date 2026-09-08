import { loadCategoryBaselines } from "@/lib/category-baselines";
import {
  loadMarketOverview,
  loadMarketTrend,
  loadOpenNeedsByCategory,
  loadProgrammeConcentration,
} from "@/lib/market-needs";

export const dynamic = "force-dynamic";

function days(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function cutoffWindow(earliest: string | null, latest: string | null): string {
  if (!earliest || !latest) return "Unavailable";
  return earliest === latest ? latest : `${earliest} to ${latest}`;
}

export default async function MarketPage() {
  const [overview, trend, baselines, openNeeds, programmeConcentration] = await Promise.all([
    loadMarketOverview(),
    loadMarketTrend(),
    loadCategoryBaselines(),
    loadOpenNeedsByCategory(),
    loadProgrammeConcentration(),
  ]);

  const productionUnavailable = overview === null;

  return <>
    <p className="small">Market Intelligence</p>
    <h1 className="h1">Current procurement runway across the indexed Lombardia project set</h1>
    <p className="lede">
      Production aggregates are calculated from the current funded-project, component and assessment ledgers.
      Missing fields and coverage limits are shown explicitly rather than treated as zero.
    </p>

    {productionUnavailable ? (
      <div className="notice scope">
        <strong>Production market data unavailable.</strong> ProcRun does not replace unavailable production aggregates with fixtures or inferred totals.
      </div>
    ) : (
      <>
        <div className="grid">
          <div className="card"><div className="small">Indexed funded projects</div><div className="kpi">{overview.fundedProjects}</div></div>
          <div className="card"><div className="small">Projects with identified components</div><div className="kpi">{overview.projectsWithComponents}</div></div>
          <div className="card"><div className="small">Currently assessed components</div><div className="kpi">{overview.assessedComponents}</div></div>
          <div className="card"><div className="small">Current OPEN components</div><div className="kpi">{overview.openComponents}</div></div>
        </div>

        <section className="section">
          <p className="small">Current assessment state</p>
          <h2 className="h2">What the latest authoritative assessment supports</h2>
          <div style={{overflowX:"auto"}}>
            <table>
              <thead><tr><th>State</th><th>Components</th></tr></thead>
              <tbody>
                <tr><td>OPEN</td><td>{overview.openComponents}</td></tr>
                <tr><td>CLOSED</td><td>{overview.closedComponents}</td></tr>
                <tr><td>UNRESOLVED</td><td>{overview.unresolvedComponents}</td></tr>
              </tbody>
            </table>
          </div>
          <p className="micro">
            Current state comes from the latest deterministic record in <code>assessment_versions</code> for each component, not from raw observation history.
            Assessment cutoff window: {cutoffWindow(overview.earliestCutoffDate, overview.latestCutoffDate)}.
          </p>
        </section>

        <section className="section">
          <p className="small">Metadata completeness</p>
          <h2 className="h2">Missingness in projects that have identified components</h2>
          <div style={{overflowX:"auto"}}>
            <table>
              <thead><tr><th>Field</th><th>Projects missing value</th><th>Denominator</th></tr></thead>
              <tbody>
                <tr><td>Programme</td><td>{overview.missingProgrammeProjects}</td><td>{overview.projectsWithComponents}</td></tr>
                <tr><td>Approved funding</td><td>{overview.missingFundingProjects}</td><td>{overview.projectsWithComponents}</td></tr>
                <tr><td>Region</td><td>{overview.missingRegionProjects}</td><td>{overview.projectsWithComponents}</td></tr>
              </tbody>
            </table>
          </div>
          <p className="micro">Missing values are excluded only where a measure requires that field. They are never converted to zero or silently imputed.</p>
        </section>
      </>
    )}

    <section className="section">
      <p className="small">Assessment history</p>
      <h2 className="h2">State snapshots across the latest 30 published cutoff dates</h2>
      {trend === null ? (
        <p className="small">No production assessment trend is rendered without the configured database.</p>
      ) : trend.length === 0 ? (
        <p className="small">No assessment history is currently available.</p>
      ) : (
        <div style={{overflowX:"auto"}}>
          <table>
            <thead><tr><th>Cutoff</th><th>Assessed</th><th>OPEN</th><th>CLOSED</th><th>UNRESOLVED</th></tr></thead>
            <tbody>
              {trend.map((row) => <tr key={row.cutoffDate}>
                <td>{row.cutoffDate}</td>
                <td>{row.assessedComponents}</td>
                <td>{row.openComponents}</td>
                <td>{row.closedComponents}</td>
                <td>{row.unresolvedComponents}</td>
              </tr>)}
            </tbody>
          </table>
        </div>
      )}
      <p className="micro">Each row reconstructs the latest assessment known for every component as of that cutoff date. Later revisions do not overwrite earlier snapshots.</p>
    </section>

    <section className="section">
      <p className="small">Open purchasing needs across funded projects</p>
      <h2 className="h2">Where currently OPEN needs appear across the funded-project set</h2>
      <p className="small">
        Each row counts components whose latest authoritative assessment is OPEN in one exact frozen category.
        Project count is the number of distinct funded-project operation codes represented by those OPEN needs.
      </p>
      {openNeeds === null ? (
        <p className="small">No production purchasing-needs aggregation is rendered without the configured database.</p>
      ) : openNeeds.length === 0 ? (
        <p className="small">No current OPEN purchasing needs are available.</p>
      ) : (
        <div style={{overflowX:"auto"}}>
          <table>
            <thead><tr><th>Category</th><th>OPEN needs</th><th>Funded projects</th><th>Assessment cutoff</th></tr></thead>
            <tbody>
              {openNeeds.map((row) => <tr key={row.category}>
                <td>{row.category}</td>
                <td>{row.openNeeds}</td>
                <td>{row.fundedProjects}</td>
                <td>{row.earliestCutoffDate === row.latestCutoffDate ? row.latestCutoffDate : `${row.earliestCutoffDate} to ${row.latestCutoffDate}`}</td>
              </tr>)}
            </tbody>
          </table>
        </div>
      )}
      <p className="micro">Counts are ProcRun-observed states inside the indexed funded-project and TED evidence boundary. They are not a claim about total Lombardia market demand.</p>
    </section>

    <section className="section">
      <p className="small">Programme concentration of current OPEN needs</p>
      <h2 className="h2">How concentrated each category is within the funded-programme set</h2>
      {programmeConcentration === null ? (
        <p className="small">No production programme concentration is rendered without the configured database.</p>
      ) : programmeConcentration.length === 0 ? (
        <p className="small">No current OPEN needs with programme metadata are available.</p>
      ) : (
        <div style={{overflowX:"auto"}}>
          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Top programme</th>
                <th>OPEN needs in programme</th>
                <th>Share of programme-known OPEN needs</th>
                <th>Programme-known / total OPEN needs</th>
              </tr>
            </thead>
            <tbody>
              {programmeConcentration.map((row) => <tr key={row.category}>
                <td>{row.category}</td>
                <td>{row.topProgramme}</td>
                <td>{row.topProgrammeOpenNeeds}</td>
                <td>{row.topProgrammeSharePct.toFixed(1)}%</td>
                <td>{row.openNeedsWithProgramme} / {row.totalOpenNeeds}</td>
              </tr>)}
            </tbody>
          </table>
        </div>
      )}
      <p className="micro">Null programme values are excluded from the percentage denominator and disclosed through the programme-known / total count. This is not buyer concentration.</p>
    </section>

    <section className="section">
      <p className="small">Observed category baselines</p>
      <h2 className="h2">How long comparable needs stayed OPEN before a verified CLOSED observation</h2>
      <p className="small">Baselines are shown only when at least 20 completed comparable lifecycles are available. These are descriptive ProcRun-observed durations, not total project duration and not a prediction.</p>
      {baselines === null ? (
        <p className="small">No production baseline is rendered without the configured history database.</p>
      ) : baselines.length === 0 ? (
        <p className="small">No categories currently have at least 20 completed comparable OPEN-to-CLOSED histories.</p>
      ) : (
        <div style={{overflowX:"auto"}}>
          <table>
            <thead><tr><th>Category</th><th>p25 days</th><th>Median days</th><th>p75 days</th><th>n</th></tr></thead>
            <tbody>
              {baselines.map((baseline) => <tr key={baseline.category}>
                <td>{baseline.category}</td>
                <td>{days(baseline.p25Days)}</td>
                <td>{days(baseline.medianDays)}</td>
                <td>{days(baseline.p75Days)}</td>
                <td>{baseline.n}</td>
              </tr>)}
            </tbody>
          </table>
        </div>
      )}
      <p className="micro">The same n ≥ 20 minimum applies before a current OPEN opportunity receives a category percentile.</p>
    </section>

    <section className="section grid two">
      <div className="card flat"><p className="small">Coverage</p><p><strong>TED only for MVP negative search.</strong></p><p className="small">No relevant procurement found in TED as of the item cutoff does not establish absence outside TED.</p></div>
      <div className="card flat"><p className="small">Funded projects</p><p><strong>PR FESR Lombardia 2021–2027</strong></p><p className="small">The current live funded-project route is Lombardia only. Additional regions require separate source activation before customer-facing use.</p></div>
    </section>
  </>;
}
