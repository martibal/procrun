import { SupplierProfileForm } from "@/components/supplier-profile-form";
import { requireAccount } from "@/lib/auth";
import { loadAvailableCategories, loadSupplierProfile } from "@/lib/supplier-profile";

export const dynamic = "force-dynamic";

export default async function ProfilePage() {
  const { accountId } = await requireAccount();
  const [profile, categories] = await Promise.all([
    loadSupplierProfile(accountId),
    loadAvailableCategories(),
  ]);

  return <>
    <p className="small">Supplier Profile</p>
    <h1 className="h1">Define the work you want ProcRun to prioritise.</h1>
    <p className="lede">Supplier relevance is deterministic. Profile choices can filter and order opportunities; they never change evidence state and are never presented as win probability.</p>

    {categories === null ? (
      <div className="notice scope">
        <strong>Supplier Profile data unavailable.</strong> ProcRun will not substitute fixture categories or save a partial profile while the production taxonomy is unavailable.
      </div>
    ) : (
      <>
        <p className="small">No named employee, personal email address or phone number is required for the Supplier Profile.</p>
        <SupplierProfileForm
          profile={profile}
          categories={categories}
          returnTo="/app/profile"
          submitLabel="Save profile"
        />
      </>
    )}
  </>;
}
