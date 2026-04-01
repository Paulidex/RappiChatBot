import { useState } from "react";
import ImageModal from "../chat/ImageModal";

export default function InsightCard({ title, description, chartUrl, error }) {
  const [expandedImageUrl, setExpandedImageUrl] = useState(null);

  if (error) {
    return (
      <article className="bg-white shadow-md rounded-lg p-3 sm:p-4 md:p-6 border border-red-200 box-border">
        <h3 className="text-lg sm:text-xl font-semibold mb-2 text-gray-800">
          {title}
        </h3>
        <p className="text-xs sm:text-sm text-gray-600 mb-3 sm:mb-4">
          {description}
        </p>
        <p
          role="alert"
          className="bg-red-50 border border-red-200 rounded-lg p-3 sm:p-4 text-red-600 text-xs sm:text-sm"
        >
          {error}
        </p>
      </article>
    );
  }

  return (
    <>
      <article className="bg-white shadow-md rounded-lg p-3 sm:p-4 md:p-6 hover:shadow-lg transition-shadow duration-300 border border-gray-100 box-border">
        <h3 className="text-lg sm:text-xl font-semibold mb-2 text-gray-800">
          {title}
        </h3>
        <p className="text-xs sm:text-sm text-gray-600 mb-3 sm:mb-4">
          {description}
        </p>

        {chartUrl && (
          <figure className="mt-4 m-0">
            <img
              src={chartUrl}
              alt={title}
              className="w-full h-auto rounded-lg cursor-pointer hover:opacity-90 transition-opacity duration-200"
              onClick={() => setExpandedImageUrl(chartUrl)}
              onError={(loadEvent) => {
                console.error("Error loading chart image:", chartUrl);
                loadEvent.currentTarget.style.display = "none";
              }}
            />
          </figure>
        )}
      </article>

      <ImageModal
        imageUrl={expandedImageUrl}
        onClose={() => setExpandedImageUrl(null)}
      />
    </>
  );
}
