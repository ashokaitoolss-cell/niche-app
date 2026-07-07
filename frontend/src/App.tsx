import { useEffect, useState } from "react";
import PillSwitcher from "./components/PillSwitcher";
import CardStack from "./components/CardStack";
import IdeaBanner from "./components/IdeaBanner";
import { fetchLatestIdea } from "./api";
import type { FeedName, NicheIdea } from "./types";

export default function App() {
  const [feed, setFeed] = useState<FeedName>("research");
  const [idea, setIdea] = useState<NicheIdea | null>(null);

  useEffect(() => {
    fetchLatestIdea()
      .then(setIdea)
      .catch(() => setIdea(null));
  }, []);

  return (
    <div className="h-dvh w-full bg-[#15150F] flex flex-col items-center overflow-hidden">
      <div className="w-full max-w-[430px] h-full flex flex-col px-4 pt-4 pb-2">
        <IdeaBanner idea={idea} />
        <PillSwitcher active={feed} onChange={setFeed} />
        <div className="flex-1 min-h-0">
          <CardStack feed={feed} />
        </div>
      </div>
    </div>
  );
}
