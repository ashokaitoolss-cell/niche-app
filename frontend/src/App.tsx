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
    <div className="min-h-screen bg-[#15150F] flex flex-col items-center py-6 px-4">
      <div className="w-full max-w-[390px]">
        <IdeaBanner idea={idea} />
        <PillSwitcher active={feed} onChange={setFeed} />
        <CardStack feed={feed} />
      </div>
    </div>
  );
}
