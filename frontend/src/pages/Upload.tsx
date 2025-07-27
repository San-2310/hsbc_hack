import React, { useState } from "react";
import toast from "react-hot-toast";
import EnhancedUpload from "../components/Upload/EnhancedUpload";

const Upload: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  const handleUploadSuccess = (fileId: string) => {
    setUploadedFiles((prev) => [...prev, fileId]);
    toast.success(`File ${fileId} uploaded successfully!`);
  };

  const handleUploadError = (error: string) => {
    toast.error(`Upload failed: ${error}`);
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-hsbc-red to-hsbc-blue rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Enhanced Data Upload</h1>
        <p className="text-white/80">
          Upload data from files, APIs, URLs, or direct JSON input
        </p>
      </div>

      <EnhancedUpload
        onUploadSuccess={handleUploadSuccess}
        onUploadError={handleUploadError}
      />

      {uploadedFiles.length > 0 && (
        <div className="card-hsbc p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recently Uploaded Files
          </h3>
          <div className="space-y-2">
            {uploadedFiles.map((fileId, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded"
              >
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  File ID: {fileId}
                </span>
                <span className="text-xs text-green-600 bg-green-100 dark:bg-green-900/20 px-2 py-1 rounded">
                  Uploaded
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Upload;
