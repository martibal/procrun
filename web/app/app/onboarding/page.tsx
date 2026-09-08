import { redirect } from "next/navigation";

import { SupplierProfileForm } from "@/components/supplier-profile-form";
import { requireAccount } from "@/lib/auth";
import { loadAvailableCategories, loadSupplierProfile } from "@/lib/supplier-profile";

export const dynamic = "force-dynamic";

export default async function OnboardingPage() {
  const { accountId } = await requireAccount();
  const [profile, categories] = await Promise.all([
    loadSupplierProfile(accountId),
    loadAvailableCategories(),
  ]);

  if (profile) redirect("/app");

  return <>
    <p className="small">Supplier Profile onboarding</p>
    <h1 className="h1">Tell ProcRun what your company supplies.</h1>
    <p className="lede">These choices determine relevance and filtering only. They never change source evidence, procurement state or the customer-safe data boundary.</p>

    {categories === null ? (
      <div className="notice scope">
        <strong>Supplier Profile data unavailable.</strong> Onboarding stays blocked until the production taxonomy can be loaded safely.
      </div>
    ) : (
      <>
        <p className="small">No named employee, personal email address or phone number is requested.</p>
        <SupplierProfileForm
          profile={null}
          categories={categories}
          returnTo="/app"
          submitLabel="Save profile and open Opportunities"
        />
      </>
    )}
  </>;
}
