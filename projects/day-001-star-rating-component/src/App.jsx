import React, { useState } from 'react';
import StarRating from './StarRating';

function App() {
  const [currentRating, setCurrentRating] = useState(0);

  const handleRatingChange = (rating) => {
    setCurrentRating(rating);
    console.log(`User rated: ${rating} stars`);
  };

  return (
    <div className="App flex flex-col items-center justify-center p-8 bg-white shadow-lg rounded-xl max-w-md mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Rate Our Service!</h1>
      <StarRating count={5} initialRating={currentRating} onRatingChange={handleRatingChange} />
      <p className="mt-6 text-lg text-gray-700">
        You have rated: <span className="font-semibold text-indigo-600">{currentRating} out of 5</span> stars.
      </p>
    </div>
  );
}

export default App;
