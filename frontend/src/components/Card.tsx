import { motion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';
import { cn } from '../utils/cn';

interface CardProps extends HTMLMotionProps<'div'> {
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const Card = ({ children, className = '', noPadding = false, ...props }: CardProps) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={cn(
        "bg-white dark:bg-slate-900 rounded-2xl shadow-sm hover:shadow-md border border-slate-200 dark:border-slate-800 transition-all duration-300",
        !noPadding && "p-6",
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
};
