import React from 'react';
import { motion } from 'framer-motion';

export default function StatsCard({ title, value, subtitle, icon: Icon, color, trend }) {
  const colorClasses = {
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    rose: 'bg-rose-50 text-rose-600 border-rose-100',
  };

  const iconBgClasses = {
    emerald: 'bg-emerald-100',
    blue: 'bg-blue-100',
    purple: 'bg-purple-100',
    amber: 'bg-amber-100',
    rose: 'bg-rose-100',
  };

  return (
    <motion.div
      whileHover={{ y: -4 }}
      className={`bg-white rounded-2xl p-5 border ${colorClasses[color]} shadow-sm`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-slate-500 text-sm font-medium">{title}</p>
          <p className="text-2xl md:text-3xl font-bold text-slate-800 mt-1">{value}</p>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <p className={`text-xs mt-2 ${trend > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% from yesterday
            </p>
          )}
        </div>
        <div className={`w-12 h-12 rounded-xl ${iconBgClasses[color]} flex items-center justify-center`}>
          <Icon className={`w-6 h-6 ${colorClasses[color].split(' ')[1]}`} />
        </div>
      </div>
    </motion.div>
  );
}