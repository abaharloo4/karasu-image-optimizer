import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { RefreshCw, Download, ArrowLeft, Eye, EyeOff, CheckCircle, XCircle, Loader } from 'lucide-react';

export default function HistoryPanel({ onBack }) {
  const { t } = useTranslation();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedJobId, setExpandedJobId] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/history?_cb=${Date.now()}`);
      setHistory(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || 'Failed to fetch history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const toggleExpandJob = (jobId) => {
    setExpandedJobId(prev => (prev === jobId ? null : jobId));
  };

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

  const getStatusBadge = (status) => {
    switch (status) {
      case 'done':
        return (
          <span className="inline-flex items-center space-x-1 rtl:space-x-reverse px-2.5 py-1 bg-green-50 dark:bg-green-950/30 text-green-600 dark:text-green-400 text-xs font-bold rounded-lg border border-green-100 dark:border-green-900/40">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>{t('history.success')}</span>
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center space-x-1 rtl:space-x-reverse px-2.5 py-1 bg-blue-50 dark:bg-blue-950/30 text-blue-600 dark:text-blue-400 text-xs font-bold rounded-lg border border-blue-100 dark:border-blue-900/40 animate-pulse">
            <Loader className="w-3.5 h-3.5 animate-spin" />
            <span>{t('actions.processing')}</span>
          </span>
        );
      case 'error':
      default:
        return (
          <span className="inline-flex items-center space-x-1 rtl:space-x-reverse px-2.5 py-1 bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 text-xs font-bold rounded-lg border border-red-100 dark:border-red-900/40">
            <XCircle className="w-3.5 h-3.5" />
            <span>{t('history.failed')}</span>
          </span>
        );
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Top action bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center space-x-2 rtl:space-x-reverse px-4 py-2.5 bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-850 hover:bg-gray-50 dark:hover:bg-gray-700/60 rounded-xl text-xs font-black shadow-sm text-gray-700 dark:text-gray-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 rtl:rotate-180" />
          <span>{t('history.back_to_optimizer')}</span>
        </button>

        <h2 className="text-lg md:text-xl font-black bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
          {t('history.title')}
        </h2>

        <button
          onClick={fetchHistory}
          disabled={loading}
          className="flex items-center space-x-1.5 rtl:space-x-reverse px-4 py-2.5 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/40 dark:hover:bg-blue-900/40 text-blue-650 dark:text-blue-400 border border-blue-100 dark:border-blue-900/30 rounded-xl text-xs font-black transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{t('history.refresh')}</span>
        </button>
      </div>

      {/* Main panel */}
      <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-800/80 rounded-3xl p-5 shadow-sm">
        {loading && history.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 space-y-3">
            <Loader className="w-8 h-8 text-blue-500 animate-spin" />
            <p className="text-sm font-bold text-gray-500">{t('actions.processing')}</p>
          </div>
        ) : error ? (
          <div className="py-12 text-center text-red-500 font-bold text-sm">
            {error}
          </div>
        ) : history.length === 0 ? (
          <div className="py-16 text-center text-gray-450 dark:text-gray-500 font-bold text-sm">
            {t('history.no_data')}
          </div>
        ) : (
          <div className="overflow-hidden rounded-2xl border border-gray-100 dark:border-gray-700/60">
            <div className="overflow-x-auto">
              <table className="w-full text-left rtl:text-right border-collapse">
                <thead>
                  <tr className="bg-gray-50 dark:bg-gray-850/60 border-b border-gray-100 dark:border-gray-750 text-xs font-bold text-gray-500 dark:text-gray-400">
                    <th className="p-4">{t('history.job_id')}</th>
                    <th className="p-4">{t('history.status')}</th>
                    <th className="p-4">{t('history.progress')}</th>
                    <th className="p-4 text-center">{t('history.actions')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-700/50">
                  {history.map((job) => {
                    const isExpanded = expandedJobId === job.job_id;
                    const results = job.results || [];
                    const successCount = results.filter(r => r.success).length;
                    
                    return (
                      <React.Fragment key={job.job_id}>
                        {/* Job Row */}
                        <tr className="hover:bg-gray-50/40 dark:hover:bg-gray-700/20 text-xs text-gray-700 dark:text-gray-300 font-medium transition-colors">
                          <td className="p-4 font-mono select-all text-gray-800 dark:text-gray-200">
                            {job.job_id.substring(0, 8)}...{job.job_id.substring(job.job_id.length - 8)}
                          </td>
                          <td className="p-4">{getStatusBadge(job.status)}</td>
                          <td className="p-4 font-bold">
                            {job.status === 'done' ? `${successCount} / ${job.total}` : `${job.progress} / ${job.total}`}
                          </td>
                          <td className="p-4 flex items-center justify-center space-x-2 rtl:space-x-reverse">
                            <button
                              onClick={() => toggleExpandJob(job.job_id)}
                              className="flex items-center space-x-1 rtl:space-x-reverse px-3 py-1.5 border border-gray-200 dark:border-gray-750 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/60 font-bold transition-all"
                            >
                              {isExpanded ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                              <span>{isExpanded ? t('history.hide_files') : t('history.view_files')}</span>
                            </button>

                            {job.status === 'done' && successCount > 0 && (
                              <a
                                href={`/api/download/zip/${job.job_id}`}
                                className="flex items-center space-x-1 rtl:space-x-reverse px-3 py-1.5 bg-blue-50 hover:bg-blue-100 dark:bg-blue-950/40 dark:hover:bg-blue-900/40 text-blue-650 dark:text-blue-450 border border-blue-100 dark:border-blue-900/35 rounded-lg font-bold transition-all"
                                title={t('history.download_zip')}
                              >
                                <Download className="w-3.5 h-3.5" />
                                <span>{t('history.download_zip')}</span>
                              </a>
                            )}
                          </td>
                        </tr>

                        {/* Expanded Files Details Row */}
                        {isExpanded && (
                          <tr>
                            <td colSpan="4" className="p-4 bg-gray-50/50 dark:bg-gray-850/20">
                              <div className="p-4 bg-white dark:bg-gray-850 border border-gray-100 dark:border-gray-750 rounded-2xl space-y-3">
                                <h4 className="text-xs font-black text-gray-400 dark:text-gray-500 uppercase tracking-wider">
                                  {t('stats.title')}
                                </h4>
                                {results.length === 0 ? (
                                  <p className="text-xs text-gray-405 dark:text-gray-500 py-2 text-center">{t('history.no_data')}</p>
                                ) : (
                                  <div className="overflow-x-auto">
                                    <table className="w-full text-left rtl:text-right border-collapse text-xs">
                                      <thead>
                                        <tr className="border-b border-gray-100 dark:border-gray-700/60 text-gray-550 dark:text-gray-400 font-bold">
                                          <th className="pb-2 text-start">{t('history.file_name')}</th>
                                          <th className="pb-2 text-center">{t('history.original_size')}</th>
                                          <th className="pb-2 text-center">{t('history.optimized_size')}</th>
                                          <th className="pb-2 text-center">{t('history.ratio')}</th>
                                          <th className="pb-2 text-center">{t('history.status')}</th>
                                          <th className="pb-2 text-center">{t('history.download_file')}</th>
                                        </tr>
                                      </thead>
                                      <tbody className="divide-y divide-gray-100/50 dark:divide-gray-700/30">
                                        {results.map((res, fileIdx) => {
                                          const savedRatio = res.success ? Math.round(((res.original_size - res.new_size) / res.original_size) * 100) : 0;
                                          return (
                                            <tr key={fileIdx} className="text-gray-650 dark:text-gray-350">
                                              <td className="py-2.5 pr-2 font-bold max-w-xs truncate text-gray-800 dark:text-gray-200" title={res.name}>
                                                {res.name}
                                              </td>
                                              <td className="py-2.5 text-center font-semibold">{formatSize(res.original_size)}</td>
                                              <td className="py-2.5 text-center font-bold text-gray-800 dark:text-gray-100">
                                                {res.success ? formatSize(res.new_size) : '-'}
                                              </td>
                                              <td className="py-2.5 text-center">
                                                {res.success ? (
                                                  <span className={`font-black ${savedRatio > 0 ? 'text-green-500' : 'text-gray-450'}`}>
                                                    {savedRatio > 0 ? `${savedRatio}%` : '0%'}
                                                  </span>
                                                ) : '-'}
                                              </td>
                                              <td className="py-2.5 text-center">
                                                {res.success ? (
                                                  <span className="px-1.5 py-0.5 bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400 text-[10px] font-extrabold rounded-md border border-green-100/60 dark:border-green-900/20">
                                                    {t('history.success')}
                                                  </span>
                                                ) : (
                                                  <span className="px-1.5 py-0.5 bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 text-[10px] font-extrabold rounded-md border border-red-100/60 dark:border-red-900/20" title={res.error}>
                                                    {t('history.failed')}
                                                  </span>
                                                )}
                                              </td>
                                              <td className="py-2.5 text-center">
                                                {res.success && res.file_id && (
                                                  <a
                                                    href={`/api/download/${res.file_id}`}
                                                    className="inline-flex items-center justify-center p-1.5 bg-gray-50 hover:bg-gray-100 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-650 dark:text-gray-300 rounded-lg border border-gray-200/80 dark:border-gray-700/60 transition-colors"
                                                    title={t('actions.download')}
                                                  >
                                                    <Download className="w-3.5 h-3.5" />
                                                  </a>
                                                )}
                                              </td>
                                            </tr>
                                          );
                                        })}
                                      </tbody>
                                    </table>
                                  </div>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
