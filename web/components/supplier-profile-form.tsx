import { saveSupplierProfileAction } from "@/lib/supplier-profile-actions";
import type { SupplierProfile } from "@/lib/supplier-profile";

function categoryLabel(category: string): string {
  return category
    .split(":")
    .map((part) => part.replaceAll("_", " "))
    .join(" / ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function valuePreset(profile: SupplierProfile | null): string {
  if (!profile) return "any";
  if (profile.minProjectValueEur === null && profile.maxProjectValueEur === 999999) {
    return "under-1m";
  }
  if (profile.minProjectValueEur === 1000000 && profile.maxProjectValueEur === 5000000) {
    return "1m-5m";
  }
  if (profile.minProjectValueEur === 5000000 && profile.maxProjectValueEur === null) {
    return "5m-plus";
  }
  return "any";
}

export function SupplierProfileForm({
  profile,
  categories,
  returnTo,
  submitLabel,
}: {
  profile: SupplierProfile | null;
  categories: string[];
  returnTo: "/app" | "/app/profile";
  submitLabel: string;
}) {
  return (
    <form action={saveSupplierProfileAction}>
      <input type="hidden" name="returnTo" value={returnTo} />
      <div className="formgrid">
        <div className="field">
          <strong>Company name</strong>
          <label className="small" htmlFor="companyName">Company or organisation</label>
          <input
            id="companyName"
            name="companyName"
            type="text"
            required
            maxLength={160}
            defaultValue={profile?.companyName ?? ""}
            placeholder="Company name"
          />
        </div>

        <div className="field">
          <strong>Target market</strong>
          <label className="small" htmlFor="targetMarket">Launch geography</label>
          <select id="targetMarket" name="targetMarket" defaultValue="LOMBARDIA">
            <option value="LOMBARDIA">Lombardia</option>
          </select>
        </div>

        <div className="field">
          <strong>Product categories</strong>
          <p className="small">Choose one or more categories from the current ProcRun purchasing taxonomy.</p>
          <div className="checkset">
            {categories.map((category) => (
              <label className="check" key={category}>
                <input
                  type="checkbox"
                  name="category"
                  value={category}
                  defaultChecked={profile?.categoryPrefixes.includes(category) ?? false}
                />
                <span>{categoryLabel(category)}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="field">
          <strong>CPV inclusions</strong>
          <label className="small" htmlFor="cpvInclude">Optional CPV codes or families, separated by spaces or commas</label>
          <input
            id="cpvInclude"
            name="cpvInclude"
            type="text"
            inputMode="numeric"
            defaultValue={profile?.cpvInclude.join(", ") ?? ""}
            placeholder="Optional"
          />
        </div>

        <div className="field">
          <strong>CPV exclusions</strong>
          <label className="small" htmlFor="cpvExclude">Optional CPV codes or families, separated by spaces or commas</label>
          <input
            id="cpvExclude"
            name="cpvExclude"
            type="text"
            inputMode="numeric"
            defaultValue={profile?.cpvExclude.join(", ") ?? ""}
            placeholder="Optional"
          />
        </div>

        <div className="field">
          <strong>Project value</strong>
          <label className="small" htmlFor="projectValue">Optional preferred funding range</label>
          <select id="projectValue" name="projectValue" defaultValue={valuePreset(profile)}>
            <option value="any">Any value</option>
            <option value="under-1m">Under €1m</option>
            <option value="1m-5m">€1m–€5m</option>
            <option value="5m-plus">€5m+</option>
          </select>
        </div>
      </div>

      <p className="small">
        CPV constraints are optional. Where the current customer-safe OPEN record does not expose CPV,
        ProcRun withholds that match rather than inferring a CPV fit.
      </p>

      <div className="actions">
        <button className="button" type="submit">{submitLabel}</button>
      </div>
    </form>
  );
}
