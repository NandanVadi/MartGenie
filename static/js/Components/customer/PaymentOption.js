import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';

export default function PaymentOption({ icon, title, subtitle, selected, onClick }) {
  return (
    <motion.button
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`w-full p-4 rounded-2xl border-2 transition-all flex items-center gap-4 ${
        selected 
          ? 'border-emerald-500 bg-emerald-50' 
          : 'border-slate-200 bg-white hover:border-slate-300'
      }`}
    >
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
        selected ? 'bg-emerald-500 text-white' : 'bg-slate-100 text-slate-600'
      }`}>
        {icon}
      </div>
      <div className="flex-1 text-left">
        <h3 className="font-semibold text-slate-800">{title}</h3>
        <p className="text-sm text-slate-500">{subtitle}</p>
      </div>
      {selected && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center"
        >
          <Check className="w-4 h-4 text-white" />
        </motion.div>
      )}
    </motion.button>
  );
}