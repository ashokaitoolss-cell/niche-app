import type { FeedName } from "../types";
import { IconCpu, IconDeviceMobile } from "./Icons";

interface Props {
  active: FeedName;
  onChange: (feed: FeedName) => void;
}

const PILLS: { feed: FeedName; label: string; Icon: typeof IconCpu }[] = [
  { feed: "research", label: "Semiconductor", Icon: IconCpu },
  { feed: "market", label: "Consumer AI", Icon: IconDeviceMobile },
];

const ACTIVE_STYLES: Record<FeedName, { bg: string; text: string; border: string }> = {
  research: { bg: "#0F6E56", text: "#E1F5EE", border: "#1D9E75" },
  market: { bg: "#D85A30", text: "#FAECE7", border: "#D85A30" },
};

const INACTIVE_TEXT: Record<FeedName, string> = {
  research: "#5DCAA5",
  market: "#F0997B",
};

export default function PillSwitcher({ active, onChange }: Props) {
  return (
    <div className="flex gap-2 mb-5">
      {PILLS.map(({ feed, label, Icon }) => {
        const isActive = feed === active;
        const activeStyle = ACTIVE_STYLES[feed];
        return (
          <button
            key={feed}
            onClick={() => onChange(feed)}
            className="flex-1 flex items-center justify-center gap-1.5 rounded-full py-2.5 text-sm font-medium transition-colors"
            style={{
              background: isActive ? activeStyle.bg : "transparent",
              color: isActive ? activeStyle.text : INACTIVE_TEXT[feed],
              border: `1.5px solid ${activeStyle.border}`,
            }}
          >
            <Icon size={15} />
            {label}
          </button>
        );
      })}
    </div>
  );
}
