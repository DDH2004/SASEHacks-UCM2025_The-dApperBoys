import React, { useEffect, useState } from 'react';

interface PopUpProps {
  isVisible: boolean;
  onClose: () => void;
  points: number | null;
}

const PopUp: React.FC<PopUpProps> = ({ isVisible, onClose, points }) => {
  const [progress, setProgress] = useState(100); // Progress starts at 100%

  useEffect(() => {
    if (isVisible) {
      setProgress(100); // Reset progress when modal becomes visible

      const interval = setInterval(() => {
        setProgress((prev) => Math.max(prev - 2, 0)); // Decrease progress by 2% every 100ms
      }, 100);

      const timer = setTimeout(() => {
        onClose(); // Automatically close the modal after 5 seconds
      }, 5000);

      return () => {
        clearInterval(interval); // Clear interval when modal unmounts or closes
        clearTimeout(timer);
      };
    }
  }, [isVisible, onClose]);

  if (!isVisible) return null;

  return (
    <div className="fixed top-20 right-4 z-50 bg-green-800 text-white rounded-lg shadow-lg p-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-bold">Points Awarded</h3>
      </div>
      <p className="mt-2 text-sm">
        Your wallet has accumulated <span className="font-bold">{points}</span> points!
      </p>
      {/* Progress Bar */}
      <div className="relative w-full h-2 bg-gray-600 rounded-full mt-4 overflow-hidden">
        <div
          className="absolute top-0 left-0 h-full bg-green-400 transition-all"
          style={{ width: `${progress}%` }} // Dynamic width based on progress
        ></div>
      </div>
    </div>
  );
};

export default PopUp;
