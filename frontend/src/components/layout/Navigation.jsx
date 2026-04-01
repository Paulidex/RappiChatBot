import chatSvg from "../../assets/chat.svg?raw";
import insightSvg from "../../assets/insight.svg?raw";
import text from "../../constants/text.json";

const NAV_TABS = [
  { id: "chat", label: text.navigation.chat, svg: chatSvg },
  { id: "insights", label: text.navigation.insights, svg: insightSvg },
];

function getTabClassName(isActive) {
  const base =
    "flex items-center gap-1 sm:gap-2 px-3 sm:px-4 md:px-6 py-2 sm:py-2.5 md:py-3 rounded-xl text-sm sm:text-base";
  const active =
    "bg-linear-to-r from-[#fd6331] to-[#ff3e53] text-white shadow-md";
  const inactive = "text-gray-600 hover:bg-gray-50";
  return `${base} ${isActive ? active : inactive}`;
}

export default function Navigation({ activeTab, onTabChange }) {
  return (
    <nav className="col-span-1 rounded-xl bg-white shadow-md w-full box-border">
      <ul className="p-2 sm:p-3 md:p-4 gap-2 sm:gap-3 md:gap-4 flex flex-row flex-wrap list-none m-0">
        {NAV_TABS.map((tab) => (
          <li key={tab.id}>
            <button
              onClick={() => onTabChange(tab.id)}
              className={getTabClassName(activeTab === tab.id)}
            >
              <span
                className="shrink-0"
                dangerouslySetInnerHTML={{ __html: tab.svg }}
              />
              <span className="whitespace-nowrap">{tab.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}
