import text from "../../constants/text.json";

export default function TypingIndicator() {
  return (
    <li className="flex justify-start" role="status" aria-label={text.chat.typingLabel}>
      <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3">
        <div className="flex gap-1" aria-hidden="true">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: "150ms" }}
          />
          <span
            className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
            style={{ animationDelay: "300ms" }}
          />
        </div>
      </div>
    </li>
  );
}
