import React from 'react';
import { motion } from 'framer-motion';

export default function QRCode({ data, size = 200 }) {
  // Generate a simple visual QR pattern (decorative)
  const generatePattern = () => {
    const cells = [];
    const gridSize = 21;
    
    for (let i = 0; i < gridSize; i++) {
      for (let j = 0; j < gridSize; j++) {
        // Position patterns (corners)
        const isCorner = 
          (i < 7 && j < 7) || 
          (i < 7 && j >= gridSize - 7) || 
          (i >= gridSize - 7 && j < 7);
        
        // Random fill for data area
        const isFilled = isCorner 
          ? (i < 7 && j < 7 && (i < 1 || i > 5 || j < 1 || j > 5 || (i > 1 && i < 5 && j > 1 && j < 5))) ||
            (i < 7 && j >= gridSize - 7 && (i < 1 || i > 5 || j < gridSize - 6 || j > gridSize - 2 || (i > 1 && i < 5 && j > gridSize - 6 && j < gridSize - 2))) ||
            (i >= gridSize - 7 && j < 7 && (i < gridSize - 6 || i > gridSize - 2 || j < 1 || j > 5 || (i > gridSize - 6 && i < gridSize - 2 && j > 1 && j < 5)))
          : Math.random() > 0.5;

        if (isFilled) {
          cells.push({ x: j, y: i });
        }
      }
    }
    return cells;
  };

  const [cells] = React.useState(generatePattern);
  const cellSize = size / 21;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2, type: "spring" }}
      className="relative"
    >
      <div className="bg-white p-4 rounded-2xl shadow-lg">
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {cells.map((cell, i) => (
            <motion.rect
              key={i}
              x={cell.x * cellSize}
              y={cell.y * cellSize}
              width={cellSize - 1}
              height={cellSize - 1}
              fill="#1e293b"
              rx={1}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.001 }}
            />
          ))}
        </svg>
      </div>
      {/* Decorative corner */}
      <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center shadow-lg">
        <span className="text-white text-xs font-bold">QR</span>
      </div>
    </motion.div>
  );
}