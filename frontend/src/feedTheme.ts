import type { FeedName } from "./types";

export interface FeedTheme {
  accent: string;
  bg: string;
  text: string;
}

export const FEED_THEME: Record<FeedName, FeedTheme> = {
  research: { accent: "#1D9E75", bg: "#0F6E56", text: "#E1F5EE" },
  market: { accent: "#D85A30", bg: "#D85A30", text: "#FAECE7" },
};
