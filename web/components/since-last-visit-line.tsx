"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { SinceLastVisitSummary } from "@/lib/since-last-visit";

type Cached = { day: string; newMatchesCount: number; changedSavedIds: string[] };

function localDay(): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "Europe/Rome",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

function plural(value: number, one: string, many: string): string {
  return `${value} ${value === 1 ? one : many}`;
}

export function SinceLastVisitLine({ summary }: { summary: SinceLastVisitSummary | null }) {
  const storageKey = summary ? `procrun:since-last:${summary.accountId}` : null;
  const [cached, setCached] = useState<Cached | null>(null);

  useEffect(() => {
    if (!summary || !storageKey || summary.firstVisit) return;
    const today = localDay();
    if (summary.newMatchesCount !== null) {
      const next: Cached = {
        day: today,
        newMatchesCount: summary.newMatchesCount,
        changedSavedIds: summary.changedSavedIds,
      };
      localStorage.setItem(storageKey, JSON.stringify(next));
      setCached(next);
      return;
    }
    if (summary.sameDayRepeat) {
      try {
        const parsed = JSON.parse(localStorage.getItem(storageKey) ?? "null") as Cached | null;
        if (parsed?.day === today) setCached(parsed);
      } catch {
        localStorage.removeItem(storageKey);
      }
    }
  }, [storageKey, summary]);

  const counts = useMemo(() => {
    if (!summary || summary.firstVisit) return null;
    if (summary.newMatchesCount !== null) {
      return { newMatchesCount: summary.newMatchesCount, changedSavedIds: summary.changedSavedIds };
    }
    return cached;
  }, [cached, summary]);

  // First visit has no previous visit to summarize. Keep the normal feed-top copy unchanged.
  if (!summary || summary.firstVisit) return null;

  const changedCount = counts?.changedSavedIds.length ?? 0;
  const showActivity = Boolean(counts && (counts.newMatchesCount > 0 || changedCount > 0));
  const firstChanged = counts?.changedSavedIds[0];

  return (
    <div className="small" style={{ marginTop: 8, marginBottom: 18 }}>
      {showActivity ? (
        <div>
          {counts!.newMatchesCount > 0
            ? plural(counts!.newMatchesCount, "new match since your last visit", "new matches since your last visit")
            : null}
          {counts!.newMatchesCount > 0 && changedCount > 0 ? " · " : null}
          {changedCount > 0 ? (
            <Link
              className="text-link strong"
              href={`/app/saved?changed=${encodeURIComponent(firstChanged!)}#${encodeURIComponent(firstChanged!)}`}
            >
              {plural(changedCount, "saved opportunity changed status", "saved opportunities changed status")}
            </Link>
          ) : null}
        </div>
      ) : null}
      <div style={summary.freshness.stale ? { color: "var(--signal-rust, #B5482A)" } : undefined}>
        {summary.freshness.text}
      </div>
    </div>
  );
}
