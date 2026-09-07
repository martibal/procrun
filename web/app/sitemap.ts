import type { MetadataRoute } from "next";
import { getPublicShowcaseOpportunities } from "@/lib/public-showcase";
import { getPublicSiteUrl } from "@/lib/public-site-url";

export default function sitemap(): MetadataRoute.Sitemap {
  const siteUrl = getPublicSiteUrl();
  if (!siteUrl) return [];

  const staticPaths = ["/", "/demo", "/methodology", "/pricing", "/terms", "/privacy"];
  const staticEntries: MetadataRoute.Sitemap = staticPaths.map((path) => ({
    url: new URL(path, siteUrl).toString(),
  }));

  const showcaseEntries: MetadataRoute.Sitemap = getPublicShowcaseOpportunities().flatMap((item) => [
    { url: new URL(`/demo/opportunities/${item.id}`, siteUrl).toString() },
    { url: new URL(`/demo/opportunities/${item.id}/history`, siteUrl).toString() },
  ]);

  return [...staticEntries, ...showcaseEntries];
}
