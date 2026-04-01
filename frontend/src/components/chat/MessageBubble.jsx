import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import ImageModal from "./ImageModal";
import text from "../../constants/text.json";

export default function MessageBubble({ message }) {
  const [expandedImageUrl, setExpandedImageUrl] = useState(null);

  const isUserMessage = message.type === "user";

  const bubbleStyles = isUserMessage
    ? "bg-linear-to-r from-[#fd6331] to-[#ff3e53] text-white rounded-br-sm"
    : "bg-gray-100 text-gray-900 rounded-bl-sm";

  return (
    <li className={`flex ${isUserMessage ? "justify-end" : "justify-start"}`}>
      <article
        className={`max-w-full sm:max-w-xl px-3 sm:px-4 py-2 sm:py-3 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed ${bubbleStyles}`}
      >
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {message.content}
        </ReactMarkdown>

        {message.chartUrl && (
          <figure className="mt-4 m-0">
            <img
              src={message.chartUrl}
              alt={text.chat.chartAlt}
              className="cursor-pointer rounded-lg transition-transform duration-300 hover:scale-105"
              onClick={() => setExpandedImageUrl(message.chartUrl)}
            />
          </figure>
        )}
      </article>

      <ImageModal
        imageUrl={expandedImageUrl}
        onClose={() => setExpandedImageUrl(null)}
      />
    </li>
  );
}
