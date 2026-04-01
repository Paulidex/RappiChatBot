import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

export default function MessageList({ messages, isTyping, messagesEndRef }) {
  return (
    <ol className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6 space-y-3 sm:space-y-4 min-h-0 bg-white box-border list-none m-0">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isTyping && <TypingIndicator />}

      <li ref={messagesEndRef} aria-hidden="true" className="h-0" />
    </ol>
  );
}
