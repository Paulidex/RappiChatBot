import { useChat } from "../../hooks/useChat";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";

export default function ChatView({ visible }) {
  const {
    messages,
    inputText,
    isTyping,
    isGenerating,
    messagesEndRef,
    setInputText,
    sendMessage,
    exportPdf,
  } = useChat();

  return (
    <section
      className={`w-full h-full bg-white rounded-2xl flex-col box-border ${
        visible ? "flex" : "hidden"
      }`}
    >
      <MessageList
        messages={messages}
        isTyping={isTyping}
        messagesEndRef={messagesEndRef}
      />
      <ChatInput
        inputText={inputText}
        isGenerating={isGenerating}
        onInputChange={setInputText}
        onSend={sendMessage}
        onExportPdf={exportPdf}
      />
    </section>
  );
}
