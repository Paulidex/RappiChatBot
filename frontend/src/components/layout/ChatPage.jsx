import ChatView from "../chat/ChatView";
import InsightPanel from "../insights/InsightPanel";

export default function ChatLayout({ activeTab }) {
  return (
    <main className="row-span-3 row-start-3 bg-white rounded-xl shadow-md flex flex-col overflow-hidden w-full h-full box-border">
      <ChatView visible={activeTab === "chat"} />
      <InsightPanel visible={activeTab === "insights"} />
    </main>
  );
}
