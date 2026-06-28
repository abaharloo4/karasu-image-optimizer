import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { UploadCloud, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function DropZone({ onUploadComplete, onError }) {
  const { t } = useTranslation();
  const [isDragActive, setIsDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const processFiles = async (files) => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      // Validate that it is an image
      if (files[i].type.startsWith('image/')) {
        formData.append('files', files[i]);
      }
    }

    try {
      // We send request to /api/upload
      // Vite proxy will route it to http://localhost:5000/api/upload
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      onUploadComplete(response.data);
    } catch (err) {
      console.error(err);
      onError(err.response?.data?.error || t('status.error'));
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFiles(e.target.files);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      onClick={onButtonClick}
      className={`relative w-full py-12 px-4 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center cursor-pointer transition-all duration-300 ${
        isDragActive
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20 scale-[0.99]'
          : 'border-gray-300 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-gray-50 dark:hover:bg-gray-800/20'
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*"
        onChange={handleChange}
        className="hidden"
      />
      
      {isUploading ? (
        <div className="flex flex-col items-center space-y-3 pointer-events-none">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
          <p className="text-sm font-semibold text-gray-600 dark:text-gray-300">
            {t('status.uploading')}
          </p>
        </div>
      ) : (
        <div className="flex flex-col items-center space-y-3 text-center pointer-events-none">
          <div className="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full">
            <UploadCloud className="w-10 h-10" />
          </div>
          <div className="space-y-1">
            <p className="text-base font-bold text-gray-800 dark:text-gray-200">
              {t('actions.drag_drop')}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              PNG, JPEG, WEBP, GIF (Max 200MB)
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
