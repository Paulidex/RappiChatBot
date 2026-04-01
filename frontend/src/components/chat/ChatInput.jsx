import sendSvg from "../../assets/send.svg?raw";
import stopSvg from "../../assets/stop.svg?raw";
import { ENDPOINTS } from "../../constants/endpoints";
import text from "../../constants/text.json";

function autoResizeTextarea(textareaElement) {
  textareaElement.style.height = "auto";
  textareaElement.style.height = textareaElement.scrollHeight + "px";
}

export default function ChatInput({ inputText, isGenerating, onInputChange, onSend }) {
  function handleTextareaChange(changeEvent) {
    onInputChange(changeEvent.target.value);
    autoResizeTextarea(changeEvent.target);
  }

  function handleKeyDown(keyboardEvent) {
    if (keyboardEvent.key !== "Enter") {
      return;
    }

    if (keyboardEvent.shiftKey) {
      setTimeout(function () {
        autoResizeTextarea(keyboardEvent.target);
        keyboardEvent.target.scrollTop = keyboardEvent.target.scrollHeight;
      }, 0);
    } else {
      keyboardEvent.preventDefault();
      onSend();
    }
  }

  function handleFormSubmit(formEvent) {
    formEvent.preventDefault();
    onSend();
  }

  function handleGeneratePdf() {
    window.open(ENDPOINTS.generatePdf, "_blank");
  }

  let sendButtonStyles = "";
  if (isGenerating) {
    sendButtonStyles = "bg-gray-300 text-gray-800 hover:bg-gray-400";
  } else {
    sendButtonStyles = "bg-linear-to-r from-[#fd6331] to-[#ff3e53] text-white hover:opacity-90";
  }

  let currentIcon = "";
  if (isGenerating) {
    currentIcon = stopSvg;
  } else {
    currentIcon = sendSvg;
  }

  let buttonLabel = "";
  if (isGenerating) {
    buttonLabel = text.chat.stopButton;
  } else {
    buttonLabel = text.chat.sendButton;
  }

  return (
    <footer className="bg-white p-2 sm:p-3 md:p-4 border-t border-gray-100 box-border">
      <form
        onSubmit={handleFormSubmit}
        className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full items-stretch sm:items-center"
      >
        <textarea
          placeholder={text.chat.inputPlaceholder}
          value={inputText}
          onChange={handleTextareaChange}
          onKeyDown={handleKeyDown}
          rows={1}
          className="flex-1 bg-gray-100 text-gray-700 placeholder-gray-500 px-3 sm:px-4 md:px-5 py-2 sm:py-2.5 md:py-3 rounded-2xl border-none outline-none focus:ring-2 focus:ring-[#fd6331]/30 transition overflow-y-auto leading-relaxed resize-none max-h-40 text-sm sm:text-base"
        />

        <div className="flex gap-2 sm:gap-3">
          <button
            type="submit"
            className={"flex-1 sm:flex-none px-4 sm:px-6 py-2 sm:py-3 rounded-2xl flex flex-row gap-1 sm:gap-2 items-center justify-center font-medium transition text-sm sm:text-base " + sendButtonStyles}
          >
            <span
              className="shrink-0"
              dangerouslySetInnerHTML={{ __html: currentIcon }}
            />
            <span className="whitespace-nowrap">{buttonLabel}</span>
          </button>

          <button
            type="button"
            onClick={handleGeneratePdf}
            className="flex-1 sm:flex-none px-4 sm:px-6 py-2 sm:py-3 rounded-2xl bg-linear-to-r from-[#f5bf7b] to-[#f39c36] hover:from-[#f39c36] hover:to-[#f5bf7b] transition-all duration-300 text-sm sm:text-base"
          >
            <span className="text-black font-semibold whitespace-nowrap">
              {text.chat.generateHistoryButton}
            </span>
          </button>
        </div>
      </form>
    </footer>
  );
}
