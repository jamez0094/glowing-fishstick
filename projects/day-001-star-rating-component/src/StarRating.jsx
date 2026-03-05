import React, { useState, useEffect } from 'react';

const StarRating = ({ count = 5, initialRating = 0, onRatingChange }) => {
  const [rating, setRating] = useState(initialRating);
  const [hoverRating, setHoverRating] = useState(0);

  useEffect(() => {
    setRating(initialRating);
  }, [initialRating]);

  const handleStarClick = (index) => {
    setRating(index);
    if (onRatingChange) {
      onRatingChange(index);
    }
  };

  const handleStarHover = (index) => {
    setHoverRating(index);
  };

  const handleStarLeave = () => {
    setHoverRating(0);
  };

  return (
    <div className="flex space-x-1">
      {[...Array(count)].map((_, index) => {
        index += 1; // Stars are 1-indexed
        return (
          <button
            key={index}
            type="button"
            className={
              `text-4xl transition-colors duration-200 focus:outline-none ` +
              ((hoverRating || rating) >= index ? 'text-yellow-400' : 'text-gray-300')
            }
            onClick={() => handleStarClick(index)}
            onMouseEnter={() => handleStarHover(index)}
            onMouseLeave={handleStarLeave}
          >
            &#9733; {/* Unicode star character */}
          </button>
        );
      })}
    </div>
  );
};

export default StarRating;
