export type FeedName = "research" | "market";

export interface Summary {
  id: number;
  feed: FeedName;
  category: string | null;
  headline: string;
  summary: string;
  source_url: string;
  source_label: string;
  why_it_matters: string | null;
  mentioned_investors: string; // JSON-encoded string array
  created_at: string;
}

export interface NicheIdea {
  id: number;
  date: string;
  idea_text: string;
  source_refs: string; // JSON-encoded array of summary ids
  created_at: string;
}
