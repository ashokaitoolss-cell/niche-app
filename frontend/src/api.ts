import type { FeedName, NicheIdea, Summary } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function fetchSummaries(feed: FeedName): Promise<Summary[]> {
  const res = await fetch(`${API_BASE}/api/summaries?feed=${feed}&limit=30`);
  if (!res.ok) throw new Error(`Failed to load ${feed} summaries`);
  return res.json();
}

export async function fetchLatestIdea(): Promise<NicheIdea | null> {
  const res = await fetch(`${API_BASE}/api/niche-ideas/latest`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to load niche idea");
  return res.json();
}

export async function saveSummary(summaryId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/saved`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ summary_id: summaryId }),
  });
  if (!res.ok) throw new Error("Failed to save item");
}
