/** ShowMoreButton component.
 *
 * Button to reveal all widgets in progressive disclosure.
 * Shows count of hidden widgets.
 */

import React from 'react';

interface ShowMoreButtonProps {
  hiddenCount: number;
  onShowMore: () => void;
  isLoading?: boolean;
}

export const ShowMoreButton: React.FC<ShowMoreButtonProps> = ({
  hiddenCount,
  onShowMore,
  isLoading = false,
}) => {
  if (hiddenCount <= 0) {
    return null;
  }

  return (
    <div className="flex justify-center my-4">
      <button
        onClick={onShowMore}
        disabled={isLoading}
        className={`
          inline-flex items-center px-4 py-2
          bg-white dark:bg-gray-800
          border border-gray-300 dark:border-gray-600
          rounded-lg shadow-sm
          text-sm font-medium text-gray-700 dark:text-gray-300
          hover:bg-gray-50 dark:hover:bg-gray-700
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors duration-200
        `}
        aria-label={`Show ${hiddenCount} more widgets`}
      >
        {isLoading ? (
          <>
            <svg
              className="animate-spin -ml-1 mr-2 h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Loading...
          </>
        ) : (
          <>
            <span>Show More</span>
            <span className="ml-2 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 py-0.5 px-2 rounded-full text-xs">
              +{hiddenCount}
            </span>
          </>
        )}
      </button>
    </div>
  );
};
