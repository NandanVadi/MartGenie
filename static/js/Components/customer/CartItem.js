import React from 'react';
import { Button } from '@/components/ui/button';
import { Minus, Plus, Trash2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function CartItem({ item, onUpdateQuantity, onRemove }) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="bg-white rounded-2xl p-4 shadow-sm border border-slate-100"
    >
      <div className="flex gap-3">
        {/* Product Image */}
        <div className="w-16 h-16 rounded-xl bg-slate-100 flex-shrink-0 overflow-hidden">
          {item.image_url ? (
            <img 
              src={item.image_url} 
              alt={item.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-slate-400 text-xs">
              No image
            </div>
          )}
        </div>

        {/* Details */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-800 text-sm truncate">{item.name}</h3>
          <p className="text-emerald-600 font-bold mt-0.5">₹{item.price.toFixed(2)}</p>
          
          {/* Quantity Controls */}
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8 rounded-lg border-slate-200"
                onClick={() => onUpdateQuantity(item.quantity - 1)}
              >
                <Minus className="h-3 w-3" />
              </Button>
              <span className="w-8 text-center font-semibold text-slate-800">
                {item.quantity}
              </span>
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8 rounded-lg border-slate-200"
                onClick={() => onUpdateQuantity(item.quantity + 1)}
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="font-bold text-slate-800">
                ₹{(item.price * item.quantity).toFixed(2)}
              </span>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-red-500 hover:text-red-600 hover:bg-red-50"
                onClick={onRemove}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}