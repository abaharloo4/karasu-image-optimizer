import React from 'react';
import { useTranslation } from 'react-i18next';
import { Trash2, Eye } from 'lucide-react';

export default function FileList({ files, onDeleteFile, onSelectPreview }) {
  const { t } = useTranslation();

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  if (files.length === 0) return null;

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300">
          {t('status.ready')} ({files.length})
        </h3>
      </div>
      
      <div className="max-h-60 overflow-y-auto space-y-2 pr-1">
        {files.map((file) => (
          <div
            key={file.id}
            className="flex items-center justify-between p-3 bg-white dark:bg-gray-800/50 border border-gray-100 dark:border-gray-700/60 rounded-xl shadow-sm hover:shadow transition-shadow duration-200"
          >
            <div className="flex items-center space-x-3 rtl:space-x-reverse min-w-0">
              {file.thumb ? (
                <img
                  src={file.thumb}
                  alt={file.name}
                  className="w-12 h-12 object-cover rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900"
                />
              ) : (
                <div className="w-12 h-12 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700" />
              )}
              <div className="min-w-0">
                <p className="text-sm font-bold text-gray-800 dark:text-gray-200 truncate max-w-[200px] md:max-w-sm">
                  {file.name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {formatSize(file.size)}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-1 rtl:space-x-reverse">
              {onSelectPreview && (
                <button
                  onClick={() => onSelectPreview(file.id)}
                  title={t('actions.preview')}
                  className="p-2 text-gray-500 dark:text-gray-400 hover:text-blue-500 dark:hover:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <Eye className="w-4 h-4" />
                </button>
              )}
              <button
                onClick={() => onDeleteFile(file.id)}
                className="p-2 text-gray-500 dark:text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
