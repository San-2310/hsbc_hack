import {
  BarChart3,
  Download,
  LineChart,
  PieChart,
  Play,
  Settings,
  TrendingUp,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";

interface AggregationConfig {
  type: "group_by" | "time_series" | "pivot" | "summary_stats" | "hsbc_pattern";
  group_by?: string[];
  value_columns?: string[];
  aggregations?: Record<string, string[]>;
  date_column?: string;
  value_column?: string;
  frequency?: string;
  index?: string[];
  columns?: string[];
  values?: string[];
  pattern?: string;
  cleaning_rules?: {
    missing_values?: "drop" | "fill_mean" | "fill_mode";
    outliers?: "keep" | "remove";
    date_columns?: string[];
  };
}

interface EnhancedAggregationProps {
  fileId: string;
  schema: any;
  onAggregationComplete?: (result: any) => void;
}

const EnhancedAggregation: React.FC<EnhancedAggregationProps> = ({
  fileId,
  schema,
  onAggregationComplete,
}) => {
  const [config, setConfig] = useState<AggregationConfig>({
    type: "group_by",
    group_by: [],
    value_columns: [],
    aggregations: {},
    cleaning_rules: {
      missing_values: "drop",
      outliers: "keep",
      date_columns: [],
    },
  });
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [availableColumns, setAvailableColumns] = useState<string[]>([]);
  const [numericColumns, setNumericColumns] = useState<string[]>([]);
  const [dateColumns, setDateColumns] = useState<string[]>([]);

  useEffect(() => {
    if (schema?.column_info) {
      const columns = Object.keys(schema.column_info);
      setAvailableColumns(columns);

      const numeric = columns.filter(
        (col) => schema.column_info[col].type === "numeric"
      );
      setNumericColumns(numeric);

      const dates = columns.filter(
        (col) => schema.column_info[col].type === "datetime"
      );
      setDateColumns(dates);
    }
  }, [schema]);

  const aggregationTypes = [
    { id: "group_by", label: "Group By", icon: BarChart3 },
    { id: "time_series", label: "Time Series", icon: LineChart },
    { id: "pivot", label: "Pivot Table", icon: PieChart },
    { id: "summary_stats", label: "Summary Stats", icon: TrendingUp },
    { id: "hsbc_pattern", label: "HSBC Patterns", icon: Settings },
  ];

  const hsbcPatterns = [
    { id: "transaction_summary", label: "Transaction Summary" },
    { id: "customer_summary", label: "Customer Summary" },
    { id: "regional_summary", label: "Regional Summary" },
  ];

  const aggregationFunctions = [
    "sum",
    "mean",
    "median",
    "min",
    "max",
    "count",
    "std",
    "var",
    "first",
    "last",
    "unique_count",
  ];

  const timeFrequencies = [
    { value: "D", label: "Daily" },
    { value: "W", label: "Weekly" },
    { value: "M", label: "Monthly" },
    { value: "Q", label: "Quarterly" },
    { value: "Y", label: "Yearly" },
  ];

  const handleAggregation = async () => {
    setProcessing(true);

    try {
      const response = await fetch("/api/enhanced-processing/aggregate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("firebase_token")}`,
        },
        body: JSON.stringify({
          file_id: fileId,
          config: config,
        }),
      });

      const result = await response.json();

      if (result.status === "success") {
        setResult(result.data);
        onAggregationComplete?.(result.data);
        toast.success("Aggregation completed successfully!");
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Aggregation failed";
      toast.error(errorMessage);
    } finally {
      setProcessing(false);
    }
  };

  const handleExport = async () => {
    if (!result) return;

    try {
      const response = await fetch("/api/enhanced-processing/export", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("firebase_token")}`,
        },
        body: JSON.stringify({
          file_id: fileId,
          aggregation_result: result,
          format: "csv",
        }),
      });

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `aggregation_${fileId}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);

      toast.success("Export completed!");
    } catch (error) {
      toast.error("Export failed");
    }
  };

  const updateConfig = (updates: Partial<AggregationConfig>) => {
    setConfig((prev) => ({ ...prev, ...updates }));
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      {/* Configuration Panel */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
        <div className="border-b border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Aggregation Configuration
          </h3>
        </div>

        <div className="p-6 space-y-6">
          {/* Aggregation Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Aggregation Type
            </label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {aggregationTypes.map((type) => {
                const Icon = type.icon;
                return (
                  <button
                    key={type.id}
                    onClick={() => updateConfig({ type: type.id as any })}
                    className={`flex flex-col items-center p-4 rounded-lg border-2 transition-colors ${
                      config.type === type.id
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                        : "border-gray-200 dark:border-gray-600 hover:border-gray-300"
                    }`}
                  >
                    <Icon className="w-6 h-6 mb-2" />
                    <span className="text-sm font-medium">{type.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* HSBC Pattern Selection */}
          {config.type === "hsbc_pattern" && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                HSBC Pattern
              </label>
              <select
                value={config.pattern || ""}
                onChange={(e) => updateConfig({ pattern: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a pattern</option>
                {hsbcPatterns.map((pattern) => (
                  <option key={pattern.id} value={pattern.id}>
                    {pattern.label}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Group By Configuration */}
          {config.type === "group_by" && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Group By Columns
                </label>
                <select
                  multiple
                  value={config.group_by || []}
                  onChange={(e) => {
                    const selected = Array.from(
                      e.target.selectedOptions,
                      (option) => option.value
                    );
                    updateConfig({ group_by: selected });
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  size={5}
                >
                  {availableColumns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Value Columns
                </label>
                <select
                  multiple
                  value={config.value_columns || []}
                  onChange={(e) => {
                    const selected = Array.from(
                      e.target.selectedOptions,
                      (option) => option.value
                    );
                    updateConfig({ value_columns: selected });
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  size={5}
                >
                  {numericColumns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Time Series Configuration */}
          {config.type === "time_series" && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Date Column
                </label>
                <select
                  value={config.date_column || ""}
                  onChange={(e) =>
                    updateConfig({ date_column: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select date column</option>
                  {dateColumns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Value Column
                </label>
                <select
                  value={config.value_column || ""}
                  onChange={(e) =>
                    updateConfig({ value_column: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select value column</option>
                  {numericColumns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Frequency
                </label>
                <select
                  value={config.frequency || "D"}
                  onChange={(e) => updateConfig({ frequency: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {timeFrequencies.map((freq) => (
                    <option key={freq.value} value={freq.value}>
                      {freq.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Pivot Configuration */}
          {config.type === "pivot" && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Index (Rows)
                </label>
                <select
                  multiple
                  value={config.index || []}
                  onChange={(e) => {
                    const selected = Array.from(
                      e.target.selectedOptions,
                      (option) => option.value
                    );
                    updateConfig({ index: selected });
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  size={4}
                >
                  {availableColumns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Columns
                </label>
                <select
                  value={config.columns?.[0] || ""}
                  onChange={(e) => updateConfig({ columns: [e.target.value] })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select column</option>
                  {availableColumns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Values
                </label>
                <select
                  value={config.values?.[0] || ""}
                  onChange={(e) => updateConfig({ values: [e.target.value] })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select value column</option>
                  {numericColumns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Data Cleaning Rules */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
              Data Cleaning Rules
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Missing Values
                </label>
                <select
                  value={config.cleaning_rules?.missing_values || "drop"}
                  onChange={(e) =>
                    updateConfig({
                      cleaning_rules: {
                        ...config.cleaning_rules,
                        missing_values: e.target.value as any,
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="drop">Drop rows</option>
                  <option value="fill_mean">Fill with mean</option>
                  <option value="fill_mode">Fill with mode</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Outliers
                </label>
                <select
                  value={config.cleaning_rules?.outliers || "keep"}
                  onChange={(e) =>
                    updateConfig({
                      cleaning_rules: {
                        ...config.cleaning_rules,
                        outliers: e.target.value as any,
                      },
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="keep">Keep outliers</option>
                  <option value="remove">Remove outliers</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Date Columns
                </label>
                <select
                  multiple
                  value={config.cleaning_rules?.date_columns || []}
                  onChange={(e) => {
                    const selected = Array.from(
                      e.target.selectedOptions,
                      (option) => option.value
                    );
                    updateConfig({
                      cleaning_rules: {
                        ...config.cleaning_rules,
                        date_columns: selected,
                      },
                    });
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  size={3}
                >
                  {availableColumns.map((col) => (
                    <option key={col} value={col}>
                      {col}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 pt-6 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={handleAggregation}
              disabled={processing}
              className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-4 h-4 mr-2" />
              {processing ? "Processing..." : "Run Aggregation"}
            </button>

            {result && (
              <button
                onClick={handleExport}
                className="flex items-center px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                <Download className="w-4 h-4 mr-2" />
                Export Results
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Results Display */}
      {result && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
          <div className="border-b border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Aggregation Results
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {result.total_rows} rows, {result.total_columns} columns
            </p>
          </div>

          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    {result.columns?.map((col: string) => (
                      <th
                        key={col}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {result.result
                    ?.slice(0, 10)
                    .map((row: any, index: number) => (
                      <tr key={index}>
                        {result.columns?.map((col: string) => (
                          <td
                            key={col}
                            className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white"
                          >
                            {row[col]}
                          </td>
                        ))}
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>

            {result.result && result.result.length > 10 && (
              <p className="text-sm text-gray-500 mt-4 text-center">
                Showing first 10 rows of {result.result.length} total rows
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedAggregation;
