import { useState, useRef, useEffect } from "react";
import { sendMessage, exportHistoryPdf } from "../api/chat";
import text from "../constants/text.json";

const INITIAL_MESSAGE = {
  type: "bot",
  content: text.chat.initialMessage,
};

const CANCELLATION_MESSAGE = {
  type: "bot",
  content: text.chat.canceledMessage,
};

function createBotMessage(apiResponse) {
  let content = "";

  if (apiResponse.bot_response) {
    content = apiResponse.bot_response;
  } else {
    const errorDetail = apiResponse.error || text.chat.noResponseFromModel;
    content = text.chat.botConnectionError + " " + errorDetail;
  }

  return {
    type: "bot",
    content: content,
    chartUrl: apiResponse.chart_base64
      ? `data:image/png;base64,${apiResponse.chart_base64}`
      : null,
  };
}

function createServerErrorMessage(error) {
  const errorDetail = error.message || text.chat.errorConnectingToServer;
  return {
    type: "bot",
    content: text.chat.serverError + " " + errorDetail,
  };
}

export function useChat() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState([{ ...INITIAL_MESSAGE, id: 1 }]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const abortControllerRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isTyping]);

  function appendMessage(newMessage) {
    setMessages(function (previousMessages) {
      const messageWithId = { ...newMessage, id: previousMessages.length + 1 };
      return [...previousMessages, messageWithId];
    });
  }

  function stopResponse() {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsTyping(false);
    setIsGenerating(false);
  }

  async function handleSendMessage() {
    if (isGenerating) {
      stopResponse();
      return;
    }

    if (!inputText.trim()) {
      return;
    }

    appendMessage({ type: "user", content: inputText });

    const question = inputText;
    setInputText("");
    setIsTyping(true);
    setIsGenerating(true);

    try {
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const apiResponse = await sendMessage(sessionId, question, controller.signal);
      appendMessage(createBotMessage(apiResponse));
    } catch (error) {
      const wasCanceled =
        error.name === "AbortError" || error.message.includes("aborted");

      if (wasCanceled) {
        appendMessage(CANCELLATION_MESSAGE);
      } else {
        appendMessage(createServerErrorMessage(error));
      }
    } finally {
      setIsTyping(false);
      setIsGenerating(false);
    }
  }

  async function handleExportPdf() {
    await exportHistoryPdf(sessionId);
  }

  return {
    messages,
    inputText,
    isTyping,
    isGenerating,
    messagesEndRef,
    setInputText,
    sendMessage: handleSendMessage,
    exportPdf: handleExportPdf,
  };
}
