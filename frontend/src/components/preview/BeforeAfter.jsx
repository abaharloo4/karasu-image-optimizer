import React, { useState } from 'react';

export default function BeforeAfter({ originalSrc, previewSrc, className = '' }) {
  const [sliderPosition, setSliderPosition] = useState(50);

  const handleSliderChange = (e) => {
    setSliderPosition(parseFloat(e.target.value));
  };

  return (
    <div className={`relative w-full aspect-video overflow-hidden rounded-xl bg-gray-100 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 select-none ${className}`}>
      {/* Before Image (Original) - Right Side */}
      <img
        src={originalSrc}
        alt="Original"
        className="absolute inset-0 w-full h-full object-contain"
        draggable="false"
      />

      {/* After Image (Processed) - Left Side (Clipped) */}
      <img
        src={previewSrc}
        alt="Optimized Preview"
        style={{
          clipPath: `polygon(0 0, ${sliderPosition}% 0, ${sliderPosition}% 100%, 0 100%)`
        }}
        className="absolute inset-0 w-full h-full object-contain"
        draggable="false"
      />

      {/* Vertical Divider Line */}
      <div
        style={{ left: `${sliderPosition}%` }}
        className="absolute top-0 bottom-0 w-0.5 bg-blue-500 pointer-events-none transform -translate-x-1/2"
      >
        {/* Drag Handle Button */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white dark:bg-gray-800 border-2 border-blue-500 shadow-md flex items-center justify-center cursor-ew-resize">
          {/* Visual handle indicator */}
          <div className="flex space-x-0.5 rtl:space-x-reverse">
            <span className="w-0.5 h-3 bg-gray-400 dark:bg-gray-500 rounded"></span>
            <span className="w-0.5 h-3 bg-gray-400 dark:bg-gray-500 rounded"></span>
          </div>
        </div>
      </div>

      {/* Invisible Range Input for controls */}
      <input
        type="range"
        min="0"
        max="100"
        step="0.1"
        value={sliderPosition}
        onChange={handleSliderChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-10"
      />
    </div>
  );
}
