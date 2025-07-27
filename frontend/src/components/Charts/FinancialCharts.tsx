import Papa from "papaparse";
import React, { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface FinancialChartsProps {
  data: any[];
  chartType: "line" | "area" | "bar" | "scatter" | "pie" | "composed";
  xKey: string;
  yKey: string;
  width?: number;
  height?: number;
  title?: string;
  showTooltip?: boolean;
  showLegend?: boolean;
  showGrid?: boolean;
  colors?: string[];
}

const FinancialCharts: React.FC<FinancialChartsProps> = ({
  data,
  chartType,
  xKey,
  yKey,
  width = 800,
  height = 400,
  title,
  showTooltip = true,
  showLegend = true,
  showGrid = true,
  colors = ["#2196F3", "#4CAF50", "#FF9800", "#F44336", "#9C27B0"],
}) => {
  const [finalData, setFinalData] = useState<any[]>([]);

  useEffect(() => {
    const parseData = async () => {
      if (data && data.length > 0) {
        setFinalData(data);
      } else {
        try {
          const response = await fetch(
            "/Users/san_23/Desktop/hsbc_hack/backend/uploads/fd5d6f9f-c93b-4690-9ae3-e40b0d7c6963.csv"
          );
          const text = await response.text();
          const parsed = Papa.parse(text, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
          });
          if (parsed.data) {
            setFinalData(parsed.data as any[]);
          }
        } catch (err) {
          console.error("Failed to fetch fallback CSV:", err);
        }
      }
    };

    parseData();
  }, [data]);

  const processedData = useMemo(() => {
    if (!finalData || finalData.length === 0) return [];

    return finalData.map((item, index) => ({
      ...item,
      [xKey]: item[xKey] ?? index,
      [yKey]: parseFloat(item[yKey]) || 0,
      index,
    }));
  }, [finalData, xKey, yKey]);

  const renderChart = () => {
    const commonProps = {
      width,
      height,
      data: processedData,
      margin: { top: 20, right: 30, left: 20, bottom: 5 },
    };

    switch (chartType) {
      case "line":
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip />}
            {showLegend && <Legend />}
            <Line
              type="monotone"
              dataKey={yKey}
              stroke={colors[0]}
              strokeWidth={2}
              dot={{ fill: colors[0], strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        );

      case "area":
        return (
          <AreaChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip />}
            {showLegend && <Legend />}
            <Area
              type="monotone"
              dataKey={yKey}
              stroke={colors[0]}
              fill={colors[0]}
              fillOpacity={0.3}
            />
          </AreaChart>
        );

      case "bar":
        return (
          <BarChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip />}
            {showLegend && <Legend />}
            <Bar dataKey={yKey} fill={colors[0]} />
          </BarChart>
        );

      case "scatter":
        return (
          <ScatterChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip />}
            {showLegend && <Legend />}
            <Scatter dataKey={yKey} fill={colors[0]} />
          </ScatterChart>
        );

      case "pie":
        return (
          <PieChart {...commonProps}>
            {showTooltip && <Tooltip />}
            {showLegend && <Legend />}
            <Pie
              data={processedData}
              cx={width / 2}
              cy={height / 2}
              labelLine={false}
              label={({ name, percent }) =>
                `${name} ${(percent * 100).toFixed(0)}%`
              }
              outerRadius={80}
              fill="#8884d8"
              dataKey={yKey}
            >
              {processedData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={colors[index % colors.length]}
                />
              ))}
            </Pie>
          </PieChart>
        );

      case "composed":
        return (
          <ComposedChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip />}
            {showLegend && <Legend />}
            <Bar dataKey={yKey} fill={colors[0]} fillOpacity={0.3} />
            <Line
              type="monotone"
              dataKey={yKey}
              stroke={colors[1]}
              strokeWidth={2}
            />
          </ComposedChart>
        );

      default:
        return (
          <LineChart {...commonProps}>
            {showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} />
            <YAxis />
            {showTooltip && <Tooltip />}
            {showLegend && <Legend />}
            <Line
              type="monotone"
              dataKey={yKey}
              stroke={colors[0]}
              strokeWidth={2}
            />
          </LineChart>
        );
    }
  };

  if (!processedData || processedData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div className="text-center">
          <div className="text-gray-500 dark:text-gray-400 text-lg mb-2">
            No data available
          </div>
          <div className="text-gray-400 dark:text-gray-500 text-sm">
            Please upload data to visualize
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg p-6">
      {title && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
        </div>
      )}

      <div className="flex justify-center">
        <ResponsiveContainer width="100%" height={height}>
          {renderChart()}
        </ResponsiveContainer>
      </div>

      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span className="font-medium">Data Points:</span>{" "}
            {processedData.length}
          </div>
          <div>
            <span className="font-medium">Chart Type:</span> {chartType}
          </div>
          <div>
            <span className="font-medium">X-Axis:</span> {xKey}
          </div>
          <div>
            <span className="font-medium">Y-Axis:</span> {yKey}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialCharts;
