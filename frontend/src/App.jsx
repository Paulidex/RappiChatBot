import { useState } from "react";
import "./App.css";
import Header from "./components/layout/Header";
import Navigation from "./components/layout/Navigation";
import ChatLayout from "./components/layout/ChatPage";

const DEFAULT_TAB = "chat";

export default function App() {
  const [activeTab, setActiveTab] = useState(DEFAULT_TAB);

  return (
    <div className="p-2 sm:p-4 md:p-6 gap-3 sm:gap-4 md:gap-6 grid grid-cols-1 grid-rows-[auto_auto_1fr] h-screen w-full box-border overflow-hidden">
      <Header />
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      <ChatLayout activeTab={activeTab} />
    </div>
  );
}
