import { forwardRef, useState } from "react";
import type { CSSProperties } from "react";
import type { Summary } from "../types";
import type { FeedTheme } from "../feedTheme";

interface Props {
  item: Summary;
  theme: FeedTheme;
  expanded: boolean;
  style?: CSSProperties;
  onPointerDown?: (e: React.PointerEvent) => void;
  onPointerMove?: (e: React.PointerEvent) => void;
  onPointerUp?: (e: React.PointerEvent) => void;
}

const Card = forwardRef<HTMLDivElement, Props>(
  ({ item, theme, expanded, style, onPointerDown, onPointerMove, onPointerUp }, ref) => {
    const [imgFailed, setImgFailed] = useState(false);
    const showImage = Boolean(item.image_url) && !imgFailed;

    return (
      <div
        ref={ref}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        className="absolute inset-0 rounded-[20px] overflow-hidden flex flex-col touch-none select-none"
        style={{
          background: "#1F1F1A",
          border: "0.5px solid rgba(247,245,240,0.12)",
          ...style,
        }}
      >
        {showImage && (
          <img
            src={item.image_url!}
            alt=""
            className="absolute inset-0 w-full h-full object-cover"
            onError={() => setImgFailed(true)}
          />
        )}
        {showImage && (
          <div
            className="absolute inset-0"
            style={{ background: "linear-gradient(to top, rgba(10,10,8,0.92) 0%, rgba(10,10,8,0.55) 42%, rgba(10,10,8,0.05) 68%)" }}
          />
        )}
        <div style={{ height: 5, background: theme.accent, flexShrink: 0, position: "relative", zIndex: 2 }} />
        <div className="flex-1 flex flex-col justify-end p-5 overflow-y-auto relative z-10">
          <p className="font-display font-normal text-[19px] leading-tight text-paper mb-2.5">
            {item.headline}
          </p>
          <p className="text-[14px] leading-relaxed text-paper/70 mb-3.5">{item.summary}</p>
          {expanded && item.why_it_matters && (
            <p className="text-[13px] leading-relaxed text-paper/55 mb-3.5 italic">
              Why it matters: {item.why_it_matters}
            </p>
          )}
          <p
            className="font-mono text-[11px] inline-block px-2.5 py-1 rounded w-fit"
            style={{ background: theme.bg, color: theme.text }}
          >
            {item.source_label}
          </p>
        </div>
      </div>
    );
  }
);

Card.displayName = "Card";
export default Card;
