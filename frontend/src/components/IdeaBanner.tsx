import { useState } from "react";
import type { NicheIdea } from "../types";

interface Props {
  idea: NicheIdea | null;
}

export default function IdeaBanner({ idea }: Props) {
  const [open, setOpen] = useState(false);

  if (!idea) return null;

  return (
    <button
      onClick={() => setOpen((v) => !v)}
      className="w-full text-left rounded-xl mb-4 overflow-hidden"
      style={{ background: "#2A2210", border: "0.5px solid rgba(250,199,117,0.25)" }}
    >
      <div style={{ height: 4, background: "#BA7517" }} />
      <div className="p-3.5">
        <p className="font-mono text-[11px] mb-1" style={{ color: "#FAC775" }}>
          Today's niche idea
        </p>
        <p
          className="text-[14px] leading-snug text-paper"
          style={open ? undefined : { display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}
        >
          {idea.idea_text}
        </p>
      </div>
    </button>
  );
}
