import React from 'react';
import { useTranslation } from 'react-i18next';
import { Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function ProgressBar({ progress, total, status, error }) {
  const { t } = useTranslation();
  
  if (status === 'idle') return null;

  const percentage = total > 0 ? Math.round((progress / total) * 100) : 0;

  return (
    <div className="w-full p-5 bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700/60 rounded-2xl shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5 rtl:space-x-reverse min-w-0">
          {status === 'processing' && (
            <Loader2 className="w-5 h-5 text-blue-500 animate-spin flex-shrink-0" />
          )}
          {status === 'done' && (
            <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
          )}
          {status === 'error' && (
            <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
          )}
          
          <span className="text-sm font-bold text-gray-800 dark:text-gray-200 truncate">
            {status === 'processing' && t('status.processing_count', { current: progress, total })}
            {status === 'done' && t('status.done')}
            {status === 'error' && (error || t('status.error'))}
          </span>
        </div>
        <span className="text-sm font-black text-blue-600 dark:text-blue-400">
          {percentage}%
        </span>
      </div>

      <div className="w-full h-3 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          style={{ width: `${percentage}%` }}
          className={`h-full rounded-full transition-all duration-300 ease-out ${
            status === 'error'
              ? 'bg-red-500'
              : status === 'done'
              ? 'bg-green-500'
              : 'bg-blue-500 animate-pulse'
          }`}
        />
      </div>
    </div>
  );
}
