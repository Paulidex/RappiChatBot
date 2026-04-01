import text from "../../constants/text.json";

export default function ImageModal({ imageUrl, onClose }) {
  if (!imageUrl) return null;

  return (
    <dialog
      open
      className="fixed inset-0 m-0 p-0 w-screen h-screen max-w-none max-h-none bg-black/70 border-none flex items-center justify-center cursor-zoom-out z-50"
      onClick={onClose}
    >
      <figure className="m-0">
        <img
          src={imageUrl}
          alt={text.chat.expandedImageAlt}
          className="max-w-4xl max-h-[90vh] rounded-xl shadow-lg cursor-zoom-in"
        />
      </figure>
    </dialog>
  );
}
