import {
  AlertTriangle,
  BarChart3,
  FileText,
  Settings,
  TrendingUp,
  Upload,
  Users,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import CsvChartViewer from "../components/Charts/CsvChartViewer";
import RuleEngineManager from "../components/RuleEngine/RuleEngineManager";
import EnhancedUpload from "../components/Upload/EnhancedUpload";

interface DashboardStats {
  totalFiles: number;
  totalUsers: number;
  totalTransactions: number;
  flaggedTransactions: number;
}

interface FileData {
  id: string;
  filename: string;
  status: string;
  total_rows: number;
  total_columns: number;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalFiles: 0,
    totalUsers: 0,
    totalTransactions: 0,
    flaggedTransactions: 0,
  });
  const [files, setFiles] = useState<FileData[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>("");
  const [chartData, setChartData] = useState<any[]>([]);
  const [chartConfig, setChartConfig] = useState({
    type: "line" as const,
    xKey: "",
    yKey: "",
  });
  const [activeTab, setActiveTab] = useState<
    "overview" | "upload" | "rules" | "visualize"
  >("overview");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchFiles();
  }, []);
  // const sampleData = [
  //   { Date: "2024-01-01", Revenue: 5000, Expenses: 3000 },
  //   { Date: "2024-02-01", Revenue: 7000, Expenses: 4000 },
  //   { Date: "2024-03-01", Revenue: 6500, Expenses: 3500 },
  // ];
  // useEffect(() => {
  //   setChartData(sampleData);
  //   setChartConfig({
  //     type: "line",
  //     xKey: "Date",
  //     yKey: "Revenue",
  //   });
  // }, []);
  const fetchDashboardData = async () => {
    try {
      const response = await fetch("/api/dashboard/overview", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      const data = await response.json();
      if (data.status === "success") {
        setStats(data.data);
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    }
  };

  const fetchFiles = async () => {
    try {
      const response = await fetch("/api/enhanced-upload/files", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      const data = await response.json();
      if (data.status === "success") {
        setFiles(data.data);
      }
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  };

  const handleUploadSuccess = (fileId: string) => {
    toast.success(`File uploaded successfully!`);
    fetchFiles();
    setSelectedFile(fileId);
    setActiveTab("rules");
  };

  const handleUploadError = (error: string) => {
    toast.error(`Upload failed: ${error}`);
  };

  const handleRulesApplied = (results: any) => {
    toast.success("Rules applied successfully!");
    if (results.aggregation) {
      const aggregatedData = Object.values(results.aggregation).flat();
      setChartData(aggregatedData);
      setActiveTab("visualize");
    }
  };

  const handleFileSelect = async (fileId: string) => {
    setSelectedFile(fileId);
    setLoading(true);

    try {
      const response = await fetch(`/api/enhanced-upload/schema/${fileId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      const data = await response.json();
      if (data.status === "success") {
        const columns = data.data.columns || [];
        if (columns.length >= 2) {
          setChartConfig({
            type: "line",
            xKey: columns[0],
            yKey: columns[1],
          });
        }
      }
    } catch (error) {
      console.error("Error fetching file schema:", error);
    } finally {
      setLoading(false);
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Files
              </p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.totalFiles}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <Users className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Users
              </p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.totalUsers}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Transactions
              </p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.totalTransactions}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Flagged
              </p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                {stats.flaggedTransactions}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Files
          </h3>
          <div className="space-y-3">
            {files.slice(0, 5).map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                onClick={() => handleFileSelect(file.id)}
              >
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {file.filename}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {file.total_rows} rows • {file.total_columns} columns
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${
                      file.status === "completed"
                        ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                        : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                    }`}
                  >
                    {file.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Quick Actions
          </h3>
          <div className="space-y-3">
            <button
              onClick={() => setActiveTab("upload")}
              className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Upload className="h-5 w-5 mr-2" />
              Upload New File
            </button>
            <button
              onClick={() => setActiveTab("rules")}
              className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Settings className="h-5 w-5 mr-2" />
              Manage Rules
            </button>
            <button
              onClick={() => setActiveTab("visualize")}
              className="w-full flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <BarChart3 className="h-5 w-5 mr-2" />
              View Charts
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderUpload = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-hsbc-red to-hsbc-blue rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Data Upload</h1>
        <p className="text-white/80">
          Upload your financial data files for processing and analysis
        </p>
      </div>

      <EnhancedUpload
        onUploadSuccess={handleUploadSuccess}
        onUploadError={handleUploadError}
      />
    </div>
  );

  const renderRules = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Rule Engine</h1>
        <p className="text-white/80">
          Create and manage normalization, aggregation, and flag rules
        </p>
      </div>

      <RuleEngineManager
        fileId={selectedFile}
        onRulesApplied={handleRulesApplied}
      />
    </div>
  );

  // const renderVisualize = () => (
  //   <div className="space-y-6">
  //     <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg p-6 text-white">
  //       <h1 className="text-2xl font-bold mb-2">Data Visualization</h1>
  //       <p className="text-white/80">
  //         Visualize your processed data with interactive charts
  //       </p>
  //     </div>

  //     <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
  //       <div className="flex flex-wrap gap-4 mb-6">
  //         <div>
  //           <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
  //             Chart Type
  //           </label>
  //           <select
  //             value={chartConfig.type}
  //             onChange={(e) =>
  //               setChartConfig((prev) => ({
  //                 ...prev,
  //                 type: e.target.value as any,
  //               }))
  //             }
  //             className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
  //           >
  //             <option value="line">Line Chart</option>
  //             <option value="area">Area Chart</option>
  //             <option value="bar">Bar Chart</option>
  //             <option value="scatter">Scatter Plot</option>
  //             <option value="pie">Pie Chart</option>
  //             <option value="composed">Composed Chart</option>
  //           </select>
  //         </div>

  //         <div>
  //           <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
  //             X-Axis
  //           </label>
  //           <select
  //             value={chartConfig.xKey}
  //             onChange={(e) =>
  //               setChartConfig((prev) => ({ ...prev, xKey: e.target.value }))
  //             }
  //             className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
  //           >
  //             <option value="">Select X-Axis</option>
  //             {chartData.length > 0 &&
  //               Object.keys(chartData[0] || {}).map((key) => (
  //                 <option key={key} value={key}>
  //                   {key}
  //                 </option>
  //               ))}
  //           </select>
  //         </div>

  //         <div>
  //           <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
  //             Y-Axis
  //           </label>
  //           <select
  //             value={chartConfig.yKey}
  //             onChange={(e) =>
  //               setChartConfig((prev) => ({ ...prev, yKey: e.target.value }))
  //             }
  //             className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
  //           >
  //             <option value="">Select Y-Axis</option>
  //             {chartData.length > 0 &&
  //               Object.keys(chartData[0] || {}).map((key) => (
  //                 <option key={key} value={key}>
  //                   {key}
  //                 </option>
  //               ))}
  //           </select>
  //         </div>
  //       </div>

  //       <FinancialCharts
  //         data={chartData}
  //         chartType={chartConfig.type}
  //         xKey={chartConfig.xKey}
  //         yKey={chartConfig.yKey}
  //         title="Financial Data Analysis"
  //         height={400}
  //       />
  //       <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-700 rounded-lg">
  //         <div className="text-center">
  //           <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
  //           <div className="text-gray-500 dark:text-gray-400 text-lg mb-2">
  //             No data to visualize
  //           </div>
  //           <div className="text-gray-400 dark:text-gray-500 text-sm">
  //             Please upload data and apply rules to see visualizations
  //           </div>
  //         </div>
  //       </div>
  //     </div>
  //   </div>
  // );
  const renderVisualize = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">CSV Viewer</h1>
        <p className="text-white/80">
          Visualize raw uploaded CSV files directly
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <CsvChartViewer />
      </div>
    </div>
  );
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-hsbc-red to-hsbc-blue rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">HSBC Enterprise Dashboard</h1>
        <p className="text-white/80">
          Comprehensive data processing and visualization platform
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6">
            {[
              { id: "overview", label: "Overview", icon: BarChart3 },
              { id: "upload", label: "Upload", icon: Upload },
              { id: "rules", label: "Rules", icon: Settings },
              { id: "visualize", label: "Visualize", icon: TrendingUp },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === id
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                <Icon className="mr-2" size={16} />
                {label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === "overview" && renderOverview()}
          {activeTab === "upload" && renderUpload()}
          {activeTab === "rules" && renderRules()}
          {activeTab === "visualize" && renderVisualize()}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
