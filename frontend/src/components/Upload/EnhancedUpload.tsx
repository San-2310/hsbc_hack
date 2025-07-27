import {
  AlertCircle,
  CheckCircle,
  Database,
  FileText,
  Globe,
  Settings,
  Upload,
} from "lucide-react";
import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";

interface UploadConfig {
  type: "file" | "api" | "url" | "json";
  url?: string;
  method?: string;
  headers?: Record<string, string>;
  params?: Record<string, string>;
  data?: any;
}

interface EnhancedUploadProps {
  onUploadSuccess?: (fileId: string) => void;
  onUploadError?: (error: string) => void;
}

const EnhancedUpload: React.FC<EnhancedUploadProps> = ({
  onUploadSuccess,
  onUploadError,
}) => {
  const [activeTab, setActiveTab] = useState<"file" | "api" | "url" | "json">(
    "file"
  );
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [apiConfig, setApiConfig] = useState<UploadConfig>({
    type: "api",
    url: "",
    method: "GET",
    headers: {},
    params: {},
    data: {},
  });
  const [urlConfig, setUrlConfig] = useState<UploadConfig>({
    type: "url",
    url: "",
  });
  const [jsonData, setJsonData] = useState<string>("");

  // File dropzone
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    await handleFileUpload(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ],
      "application/vnd.ms-excel": [".xls"],
      "application/json": [".json"],
    },
    multiple: false,
  });

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append("file", file);
      console.log(file);

      const response = await fetch("/api/enhanced-upload/file", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("firebase_token")}`,
        },
        body: formData,
      });

      const result = await response.json();

      if (result.status === "success") {
        toast.success("File uploaded successfully!");
        onUploadSuccess?.(result.data.file_id);
        setUploadProgress(100);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Upload failed";
      toast.error(errorMessage);
      onUploadError?.(errorMessage);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleApiUpload = async () => {
    if (!apiConfig.url) {
      toast.error("API URL is required");
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const response = await fetch("/api/enhanced-upload/api", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("firebase_token")}`,
        },
        body: JSON.stringify(apiConfig),
      });

      const result = await response.json();

      if (result.status === "success") {
        toast.success("API data processing started!");
        onUploadSuccess?.(result.data.file_id);
        setUploadProgress(100);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "API upload failed";
      toast.error(errorMessage);
      onUploadError?.(errorMessage);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleUrlUpload = async () => {
    if (!urlConfig.url) {
      toast.error("URL is required");
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const response = await fetch("/api/enhanced-upload/url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("firebase_token")}`,
        },
        body: JSON.stringify(urlConfig),
      });

      const result = await response.json();

      if (result.status === "success") {
        toast.success("URL data processing started!");
        onUploadSuccess?.(result.data.file_id);
        setUploadProgress(100);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "URL upload failed";
      toast.error(errorMessage);
      onUploadError?.(errorMessage);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleJsonUpload = async () => {
    if (!jsonData.trim()) {
      toast.error("JSON data is required");
      return;
    }

    let parsedData;
    try {
      parsedData = JSON.parse(jsonData);
    } catch (error) {
      toast.error("Invalid JSON format");
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const response = await fetch("/api/enhanced-upload/json", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("firebase_token")}`,
        },
        body: JSON.stringify(parsedData),
      });

      const result = await response.json();

      if (result.status === "success") {
        toast.success("JSON data processing started!");
        onUploadSuccess?.(result.data.file_id);
        setUploadProgress(100);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "JSON upload failed";
      toast.error(errorMessage);
      onUploadError?.(errorMessage);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const tabs = [
    { id: "file", label: "File Upload", icon: FileText },
    { id: "api", label: "API Endpoint", icon: Database },
    { id: "url", label: "URL Download", icon: Globe },
    { id: "json", label: "JSON Data", icon: Settings },
  ] as const;

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center p-6">
            <Upload className="w-6 h-6 text-blue-600 mr-3" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Enhanced Data Upload
            </h2>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* File Upload Tab */}
          {activeTab === "file" && (
            <div className="space-y-6">
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                    : "border-gray-300 dark:border-gray-600 hover:border-gray-400"
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                {isDragActive ? (
                  <p className="text-blue-600">Drop the file here...</p>
                ) : (
                  <div>
                    <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                      Drag & drop a file here, or click to select
                    </p>
                    <p className="text-sm text-gray-500">
                      Supports CSV, Excel (.xlsx, .xls), and JSON files
                    </p>
                  </div>
                )}
              </div>

              {uploading && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Uploading...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* API Endpoint Tab */}
          {activeTab === "api" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    API URL
                  </label>
                  <input
                    type="url"
                    value={apiConfig.url}
                    onChange={(e) =>
                      setApiConfig({ ...apiConfig, url: e.target.value })
                    }
                    placeholder="https://api.example.com/data"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Method
                  </label>
                  <select
                    value={apiConfig.method}
                    onChange={(e) =>
                      setApiConfig({ ...apiConfig, method: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Headers (JSON)
                </label>
                <textarea
                  value={JSON.stringify(apiConfig.headers, null, 2)}
                  onChange={(e) => {
                    try {
                      const headers = JSON.parse(e.target.value);
                      setApiConfig({ ...apiConfig, headers });
                    } catch {}
                  }}
                  placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}'
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {apiConfig.method === "POST" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Request Body (JSON)
                  </label>
                  <textarea
                    value={JSON.stringify(apiConfig.data, null, 2)}
                    onChange={(e) => {
                      try {
                        const data = JSON.parse(e.target.value);
                        setApiConfig({ ...apiConfig, data });
                      } catch {}
                    }}
                    placeholder='{"key": "value"}'
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              <button
                onClick={handleApiUpload}
                disabled={uploading || !apiConfig.url}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? "Processing..." : "Fetch from API"}
              </button>
            </div>
          )}

          {/* URL Download Tab */}
          {activeTab === "url" && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  File URL
                </label>
                <input
                  type="url"
                  value={urlConfig.url}
                  onChange={(e) =>
                    setUrlConfig({ ...urlConfig, url: e.target.value })
                  }
                  placeholder="https://example.com/data.csv"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-md">
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" />
                  <div className="text-sm text-blue-800 dark:text-blue-200">
                    <p className="font-medium">Supported formats:</p>
                    <ul className="mt-1 list-disc list-inside">
                      <li>CSV files (.csv)</li>
                      <li>Excel files (.xlsx, .xls)</li>
                      <li>JSON files (.json)</li>
                    </ul>
                  </div>
                </div>
              </div>

              <button
                onClick={handleUrlUpload}
                disabled={uploading || !urlConfig.url}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? "Downloading..." : "Download & Process"}
              </button>
            </div>
          )}

          {/* JSON Data Tab */}
          {activeTab === "json" && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  JSON Data
                </label>
                <textarea
                  value={jsonData}
                  onChange={(e) => setJsonData(e.target.value)}
                  placeholder='[{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]'
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                />
              </div>

              <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-md">
                <div className="flex items-start">
                  <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-2 flex-shrink-0" />
                  <div className="text-sm text-yellow-800 dark:text-yellow-200">
                    <p className="font-medium">Note:</p>
                    <p>
                      JSON data should be an array of objects or a single object
                      that can be converted to a table format.
                    </p>
                  </div>
                </div>
              </div>

              <button
                onClick={handleJsonUpload}
                disabled={uploading || !jsonData.trim()}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? "Processing..." : "Process JSON Data"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EnhancedUpload;
