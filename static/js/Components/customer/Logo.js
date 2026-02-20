import React from 'react';
import { ShoppingBag, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Logo({ size = 'lg' }) {
  const sizes = {
    sm: { icon: 24, text: 'text-xl', sparkle: 12 },
    md: { icon: 32, text: 'text-2xl', sparkle: 14 },
    lg: { icon: 48, text: 'text-3xl', sparkle: 18 },
  };

  const s = sizes[size] || sizes.lg;

  return (
    <motion.div 
      className="flex flex-col items-center gap-2"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="relative">
        <motion.div
          className="w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-200"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          <ShoppingBag className="text-white" size={s.icon} strokeWidth={1.5} />
        </motion.div>
        <motion.div
          className="absolute -top-1 -right-1 bg-yellow-400 rounded-full p-1"
          animate={{ rotate: [0, 15, -15, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <Sparkles className="text-yellow-700" size={s.sparkle} />
        </motion.div>
      </div>
      <div className="text-center">
        <h1 className={`${s.text} font-bold text-slate-800 tracking-tight`}>
          Mart<span className="text-emerald-500">Genie</span>
        </h1>
        <p className="text-xs text-slate-500 font-medium tracking-widest uppercase mt-0.5">
          Scan, Pay & Go
        </p>
      </div>
    </motion.div>
  );
}