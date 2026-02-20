import React from 'react';
import { motion } from 'framer-motion';

export default function ScanBox({ isScanning = false, detected = false }) {
  return (
    <div className="relative w-64 h-64">
      {/* Corner brackets */}
      {['top-0 left-0', 'top-0 right-0 rotate-90', 'bottom-0 right-0 rotate-180', 'bottom-0 left-0 -rotate-90'].map((position, i) => (
        <motion.div
          key={i}
          className={`absolute ${position} w-12 h-12`}
          animate={detected ? { scale: [1, 1.1, 1] } : {}}
          transition={{ duration: 0.3 }}
        >
          <div className={`absolute top-0 left-0 w-full h-1 rounded-full ${detected ? 'bg-emerald-400' : 'bg-white'} transition-colors`} />
          <div className={`absolute top-0 left-0 w-1 h-full rounded-full ${detected ? 'bg-emerald-400' : 'bg-white'} transition-colors`} />
        </motion.div>
      ))}

      {/* Scanning line animation */}
      {isScanning && !detected && (
        <motion.div
          className="absolute left-2 right-2 h-0.5 bg-gradient-to-r from-transparent via-emerald-400 to-transparent"
          animate={{ top: ['10%', '90%', '10%'] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}

      {/* Detection pulse */}
      {detected && (
        <motion.div
          className="absolute inset-0 border-4 border-emerald-400 rounded-lg"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: [0, 1, 0], scale: [0.8, 1, 1.1] }}
          transition={{ duration: 0.5 }}
        />
      )}

      {/* Center text */}
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.p
          className={`text-sm font-medium px-3 py-1 rounded-full ${
            detected ? 'bg-emerald-500 text-white' : 'bg-black/30 text-white/80'
          }`}
          animate={detected ? { scale: [1, 1.2, 1] } : {}}
        >
          {detected ? '✓ Detected!' : 'Place barcode here'}
        </motion.p>
      </div>
    </div>
  );
}