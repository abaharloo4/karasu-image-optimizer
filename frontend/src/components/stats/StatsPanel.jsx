import React from 'react';
import { useTranslation } from 'react-i18next';
import { Download, FileArchive, RotateCcw, Check, X, ShieldAlert } from 'lucide-react';
import axios from 'axios';

export default function StatsPanel({ jobResult, onReset }) {
  const { t } = useTranslation();

  const formatSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const isNegative = bytes < 0;
    const absBytes = Math.abs(bytes);
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(absBytes) / Math.log(k));
    const formatted = parseFloat((absBytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    return isNegative ? `-${formatted}` : formatted;
  };

  const results = jobResult?.results || [];
  const total = results.length;
  const successful = results.filter(r => r.success).length;
  const failed = total - successful;

  const totalOriginal = results.reduce((acc, r) => acc + (r.success ? r.original_size : 0), 0);
  const totalNew = results.reduce((acc, r) => acc + (r.success ? r.new_size : 0), 0);
  const totalSaved = totalOriginal - totalNew;
  const avgCompression = totalOriginal > 0 ? (totalSaved / totalOriginal) * 100 : 0;
  const totalTime = results.reduce((acc, r) => acc + r.processing_time, 0);

  const handleDownloadSingle = (fileId, filename) => {
    // Navigate to single download
    window.open(`/api/download/${fileId}`, '_blank');
  };

  const handleDownloadZip = () => {
    if (!jobResult?.job_id) return;
    window.open(`/api/download/zip/${jobResult.job_id}`, '_blank');
  };

  return (
    <div className="w-full space-y-6">
      {/* Overview Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 p-4 border border-gray-100 dark:border-gray-700/60 rounded-2xl shadow-sm text-center">
          <p className="text-xs font-bold text-gray-500 dark:text-gray-400">{t('stats.total')}</p>
          <p className="text-2xl font-black text-gray-800 dark:text-gray-200 mt-1">{total}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 border border-gray-100 dark:border-gray-700/60 rounded-2xl shadow-sm text-center">
          <p className="text-xs font-bold text-gray-500 dark:text-gray-400" dir="ltr">{t('stats.success')} / {t('stats.failed')}</p>
          <p className="text-2xl font-black mt-1" dir="ltr">
            <span className="text-green-500">{successful}</span>
            <span className="text-gray-300 dark:text-gray-600 mx-1.5">/</span>
            <span className={failed > 0 ? 'text-red-500' : 'text-gray-400'}>{failed}</span>
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 border border-gray-100 dark:border-gray-700/60 rounded-2xl shadow-sm text-center">
          <p className="text-xs font-bold text-gray-500 dark:text-gray-400">{t('stats.saved')}</p>
          <p className="text-2xl font-black text-blue-500 mt-1">{formatSize(totalSaved)}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 p-4 border border-gray-100 dark:border-gray-700/60 rounded-2xl shadow-sm text-center">
          <p className="text-xs font-bold text-gray-500 dark:text-gray-400">{t('stats.avg_ratio')}</p>
          <p className="text-2xl font-black text-green-500 mt-1">{avgCompression.toFixed(1)}%</p>
        </div>
      </div>

      {/* Main Results Table */}
      <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700/60 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-4 bg-gray-50 dark:bg-gray-800/40 border-b border-gray-100 dark:border-gray-700/60 flex items-center justify-between">
          <h4 className="text-sm font-extrabold text-gray-800 dark:text-gray-200">
            📊 {t('stats.title')}
          </h4>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {t('stats.time')}: {totalTime.toFixed(2)}s
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left rtl:text-right text-xs">
            <thead className="bg-gray-50/50 dark:bg-gray-900/20 text-gray-500 dark:text-gray-400 uppercase font-black tracking-wider border-b border-gray-100 dark:border-gray-700/60">
              <tr>
                <th className="p-4 font-bold">{t('settings.format')}</th>
                <th className="p-4 font-bold">{t('stats.original_size')}</th>
                <th className="p-4 font-bold">{t('stats.optimized_size')}</th>
                <th className="p-4 font-bold">{t('stats.avg_ratio')}</th>
                <th className="p-4 font-bold text-center">دانلود</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700/50">
              {results.map((res, index) => (
                <tr key={index} className="hover:bg-gray-50/50 dark:hover:bg-gray-700/10 transition-colors">
                  <td className="p-4 font-bold text-gray-800 dark:text-gray-200 truncate max-w-[150px] md:max-w-xs">
                    {res.name}
                  </td>
                  <td className="p-4 text-gray-600 dark:text-gray-400">
                    {formatSize(res.original_size)}
                  </td>
                  <td className="p-4 text-gray-600 dark:text-gray-400">
                    {res.success ? formatSize(res.new_size) : '-'}
                  </td>
                  <td className="p-4 font-extrabold">
                    {res.success ? (
                      <span className="text-green-500">-{res.compression_ratio.toFixed(1)}%</span>
                    ) : (
                      <span className="text-red-500 flex items-center space-x-1 rtl:space-x-reverse">
                        <ShieldAlert className="w-4 h-4 inline" />
                        <span className="truncate max-w-[80px]" title={res.error}>
                          {t('status.error')}
                        </span>
                      </span>
                    )}
                  </td>
                  <td className="p-4 flex justify-center">
                    {res.success ? (
                      <button
                        onClick={() => handleDownloadSingle(res.file_id, res.name)}
                        className="p-2 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/30 dark:hover:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg transition-colors"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    ) : (
                      <div className="p-2 text-gray-300 dark:text-gray-700">
                        <X className="w-4 h-4" />
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={handleDownloadZip}
          disabled={successful === 0}
          className="flex-1 flex items-center justify-center space-x-2 rtl:space-x-reverse py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-extrabold rounded-xl shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          <FileArchive className="w-5 h-5" />
          <span>{t('actions.download_all')}</span>
        </button>
        
        <button
          onClick={onReset}
          className="flex-1 sm:flex-none flex items-center justify-center space-x-2 rtl:space-x-reverse py-3 px-6 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 font-extrabold rounded-xl transition-all duration-200"
        >
          <RotateCcw className="w-5 h-5" />
          <span>{t('actions.clear_all')}</span>
        </button>
      </div>
    </div>
  );
}
