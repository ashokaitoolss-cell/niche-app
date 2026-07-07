import { useEffect, useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import Card from "./Card";
import ActionButtons from "./ActionButtons";
import { fetchSummaries, saveSummary } from "../api";
import { FEED_THEME } from "../feedTheme";
import type { FeedName, Summary } from "../types";

interface Props {
  feed: FeedName;
}

const SWIPE_THRESHOLD = 100;
const EXPAND_THRESHOLD = -80;

export default function CardStack({ feed }: Props) {
  const [items, setItems] = useState<Summary[]>([]);
  const [index, setIndex] = useState(0);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [drag, setDrag] = useState({ x: 0, y: 0, active: false });
  const startRef = useRef({ x: 0, y: 0 });
  const theme = FEED_THEME[feed];

  useEffect(() => {
    setLoading(true);
    setError(null);
    setIndex(0);
    setExpanded(false);
    fetchSummaries(feed)
      .then(setItems)
      .catch(() => setError("Couldn't reach the digest backend."))
      .finally(() => setLoading(false));
  }, [feed]);

  const current = items[index % items.length];

  function advance() {
    setIndex((i) => i + 1);
    setExpanded(false);
    setDrag({ x: 0, y: 0, active: false });
  }

  function triggerSwipe(action: "skip" | "save") {
    if (!current) return;
    if (action === "save") {
      saveSummary(current.id).catch(() => {});
    }
    setDrag({ x: action === "save" ? 600 : -600, y: 0, active: false });
    setTimeout(advance, 240);
  }

  function toggleExpand() {
    setExpanded((v) => !v);
    setDrag({ x: 0, y: 0, active: false });
  }

  function onPointerDown(e: ReactPointerEvent) {
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
    startRef.current = { x: e.clientX, y: e.clientY };
    setDrag({ x: 0, y: 0, active: true });
  }

  function onPointerMove(e: ReactPointerEvent) {
    if (!drag.active) return;
    setDrag({ x: e.clientX - startRef.current.x, y: e.clientY - startRef.current.y, active: true });
  }

  function onPointerUp() {
    if (!drag.active) return;
    if (drag.x > SWIPE_THRESHOLD) {
      triggerSwipe("save");
    } else if (drag.x < -SWIPE_THRESHOLD) {
      triggerSwipe("skip");
    } else if (drag.y < EXPAND_THRESHOLD) {
      toggleExpand();
    } else {
      setDrag({ x: 0, y: 0, active: false });
    }
  }

  if (loading) {
    return <div className="h-full flex items-center justify-center text-paper/50 text-sm">Loading feed...</div>;
  }

  if (error) {
    return <div className="h-full flex items-center justify-center text-paper/50 text-sm px-6 text-center">{error}</div>;
  }

  if (items.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-paper/50 text-sm px-6 text-center">
        Nothing new in this feed yet — check back after the next hourly run.
      </div>
    );
  }

  const rotate = drag.x / 20;
  const opacity = 1 - Math.min(Math.abs(drag.x) / 500, 0.4);

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 relative min-h-0">
        <div
          className="absolute rounded-[20px]"
          style={{ inset: 0, top: 14, left: 6, right: 6, background: "#242420", border: "0.5px solid rgba(247,245,240,0.08)" }}
        />
        <Card
          key={current?.id}
          item={current}
          theme={theme}
          expanded={expanded}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          style={{
            transform: `translate(${drag.x}px, ${drag.y}px) rotate(${rotate}deg)`,
            opacity,
            transition: drag.active ? "none" : "transform .28s ease, opacity .28s ease",
            cursor: drag.active ? "grabbing" : "grab",
          }}
        />
      </div>
      <ActionButtons
        theme={theme}
        onSkip={() => triggerSwipe("skip")}
        onSave={() => triggerSwipe("save")}
        onExpand={toggleExpand}
      />
    </div>
  );
}
