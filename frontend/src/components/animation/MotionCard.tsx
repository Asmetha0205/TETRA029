import React from 'react';
import { motion } from 'framer-motion';

interface MotionCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export const MotionCard: React.FC<MotionCardProps> = ({ children, className = '', delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  );
};
