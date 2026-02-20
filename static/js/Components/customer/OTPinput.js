import React, { useRef, useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';

export default function OTPInput({ length = 6, value, onChange }) {
  const [otp, setOtp] = useState(new Array(length).fill(''));
  const inputRefs = useRef([]);

  useEffect(() => {
    if (value) {
      const valueArray = value.split('').slice(0, length);
      const newOtp = [...valueArray, ...new Array(length - valueArray.length).fill('')];
      setOtp(newOtp);
    }
  }, [value, length]);

  const handleChange = (index, e) => {
    const val = e.target.value;
    if (isNaN(val)) return;

    const newOtp = [...otp];
    newOtp[index] = val.slice(-1);
    setOtp(newOtp);
    onChange(newOtp.join(''));

    if (val && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').slice(0, length);
    if (!/^\d+$/.test(pastedData)) return;

    const newOtp = [...pastedData.split(''), ...new Array(length - pastedData.length).fill('')];
    setOtp(newOtp);
    onChange(newOtp.join(''));
    inputRefs.current[Math.min(pastedData.length, length - 1)]?.focus();
  };

  return (
    <div className="flex gap-2 justify-center">
      {otp.map((digit, index) => (
        <Input
          key={index}
          ref={(el) => (inputRefs.current[index] = el)}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={digit}
          onChange={(e) => handleChange(index, e)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          onPaste={handlePaste}
          className="w-11 h-12 text-center text-xl font-semibold rounded-xl border-2 border-slate-200 focus:border-emerald-500 focus:ring-emerald-500/20 transition-all"
        />
      ))}
    </div>
  );
}