import { IconBookmark, IconChevronUp, IconX } from "./Icons";
import type { FeedTheme } from "../feedTheme";

interface Props {
  theme: FeedTheme;
  onSkip: () => void;
  onSave: () => void;
  onExpand: () => void;
}

export default function ActionButtons({ theme, onSkip, onSave, onExpand }: Props) {
  return (
    <div className="flex justify-center gap-6 -mt-6 relative z-10">
      <button
        onClick={onSkip}
        aria-label="Skip"
        className="w-[52px] h-[52px] rounded-full flex items-center justify-center"
        style={{ background: "#1F1F1A", border: "0.5px solid rgba(247,245,240,0.15)", color: "#B4B2A9" }}
      >
        <IconX size={22} />
      </button>
      <button
        onClick={onSave}
        aria-label="Save"
        className="w-[60px] h-[60px] rounded-full flex items-center justify-center"
        style={{ background: theme.bg, color: theme.text }}
      >
        <IconBookmark size={24} />
      </button>
      <button
        onClick={onExpand}
        aria-label="Expand"
        className="w-[52px] h-[52px] rounded-full flex items-center justify-center"
        style={{ background: "#1F1F1A", border: "0.5px solid rgba(247,245,240,0.15)", color: "#B4B2A9" }}
      >
        <IconChevronUp size={22} />
      </button>
    </div>
  );
}
