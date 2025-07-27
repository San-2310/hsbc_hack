import Papa from "papaparse";
import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
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

const CsvChartViewer = () => {
  const [csvData, setCsvData] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [xKey, setXKey] = useState("");
  const [yKey, setYKey] = useState("");
  const [chartType, setChartType] = useState("line");
  const [filters, setFilters] = useState({});
  const [error, setError] = useState("");

  useEffect(() => {
    // Try to load from file system first, fallback to sample data
    const loadCSV = async () => {
      try {
        // Option 1: Try to read from file system (if available)
        if ((window as any).fs && (window as any).fs.readFile) {
          const csvContent = await (window as any).fs.readFile(
            "/Users/san_23/Downloads/finance.csv",
            { encoding: "utf8" }
          );
          loadCSVData(csvContent);
          return;
        }

        // Option 2: Try to fetch from public folder (if file is moved there)
        try {
          const response = await fetch("/finance.csv");
          if (response.ok) {
            const csvContent = await response.text();
            loadCSVData(csvContent);
            return;
          }
        } catch (fetchError) {
          console.log("File not found in public folder");
        }

        // Option 3: Fallback to sample data
        const sampleData = `Date,Revenue,Expenses,Profit
2023-01,5000,3000,2000
2023-02,5500,3200,2300
2023-03,6000,3500,2500
2023-04,5800,3300,2500
2023-05,6200,3600,2600
2023-06,6500,3800,2700`;
        loadCSVData(sampleData);
        setError(
          "Using sample data - to load your CSV: either upload via file input or move finance.csv to your project's public folder"
        );
      } catch (err) {
        setError(`Error loading CSV: ${err.message}`);
      }
    };

    loadCSV();
  }, []);

  const loadCSVData = (csvText) => {
    try {
      const parsed = Papa.parse(csvText.trim(), {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        delimitersToGuess: [",", "\t", "|", ";"],
      });

      if (parsed.errors && parsed.errors.length > 0) {
        setError(
          `Parse errors: ${parsed.errors.map((e) => e.message).join(", ")}`
        );
        return;
      }

      if (parsed.data && Array.isArray(parsed.data) && parsed.data.length > 0) {
        const data = parsed.data.filter((row) =>
          Object.values(row).some((val) => val !== null && val !== "")
        );

        if (data.length === 0) {
          setError("No valid data rows found");
          return;
        }

        setCsvData(data);
        const keys = Object.keys(data[0] || {}).map((key) => key.trim());
        setHeaders(keys);

        if (keys.length >= 2) {
          setXKey(keys[0]);
          setYKey(keys[1]);
        }
        setError("");
      } else {
        setError("No data found in CSV");
      }
    } catch (err) {
      setError(`Error parsing CSV: ${err.message}`);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        loadCSVData(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  const filteredData = useMemo(() => {
    return csvData.filter((row) =>
      Object.entries(filters).every(([key, value]) => {
        if (value === "") return true;
        const rowValue = row[key];
        const rowStr =
          rowValue !== null && rowValue !== undefined ? String(rowValue) : "";
        return rowStr.toLowerCase();
      })
    );
  }, [csvData, filters]);

  const colors = [
    "#8884d8",
    "#82ca9d",
    "#ffc658",
    "#ff7300",
    "#00ff00",
    "#ff00ff",
  ];

  const renderChart = () => {
    if (filteredData.length === 0 || !xKey || !yKey) {
      return (
        <div className="h-64 flex items-center justify-center text-gray-500">
          No data to display
        </div>
      );
    }

    const chartProps = {
      data: filteredData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 },
    };

    switch (chartType) {
      case "line":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart {...chartProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey={yKey}
                stroke="#8884d8"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case "area":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart {...chartProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey={yKey}
                stackId="1"
                stroke="#8884d8"
                fill="#8884d8"
              />
            </AreaChart>
          </ResponsiveContainer>
        );

      case "bar":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart {...chartProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey={yKey} fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );

      case "scatter":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart {...chartProps}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={xKey} />
              <YAxis dataKey={yKey} />
              <Tooltip />
              <Legend />
              <Scatter dataKey={yKey} fill="#8884d8" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case "pie":
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={filteredData.slice(0, 10)} // Limit to 10 items for readability
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey={yKey}
                nameKey={xKey}
              >
                {filteredData.slice(0, 10).map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return <div>Unsupported chart type</div>;
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      <h1 className="text-2xl font-bold mb-6 text-gray-800">
        CSV Data Visualizer
      </h1>

      {/* Instructions */}
      <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-medium text-blue-800 mb-2">
          To load your finance.csv file:
        </h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>
            • <strong>Option 1:</strong> Use the file upload below to select
            your CSV
          </li>
          <li>
            • <strong>Option 2:</strong> Move finance.csv to your project's
            public folder and refresh
          </li>
          <li>
            • <strong>Option 3:</strong> Copy your CSV data and paste it in the
            text area (if provided)
          </li>
        </ul>
      </div>

      {/* File Upload */}
      <div className="mb-6 p-4 border-2 border-dashed border-gray-300 rounded-lg">
        <input
          type="file"
          accept=".csv"
          onChange={handleFileUpload}
          className="mb-2"
        />
        <p className="text-sm text-gray-600">
          Upload a CSV file with headers in the first row
        </p>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Controls */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Chart Type
            </label>
            <select
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={chartType}
              onChange={(e) => setChartType(e.target.value)}
            >
              <option value="line">Line Chart</option>
              <option value="area">Area Chart</option>
              <option value="bar">Bar Chart</option>
              <option value="scatter">Scatter Plot</option>
              <option value="pie">Pie Chart</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              X-Axis
            </label>
            <select
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={xKey}
              onChange={(e) => setXKey(e.target.value)}
            >
              <option value="">Select X-Axis</option>
              {headers.map((h) => (
                <option key={h} value={h}>
                  {h}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Y-Axis
            </label>
            <select
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={yKey}
              onChange={(e) => setYKey(e.target.value)}
            >
              <option value="">Select Y-Axis</option>
              {headers.map((h) => (
                <option key={h} value={h}>
                  {h}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Filters */}
        {headers.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Filters</h3>
            <div className="flex flex-wrap gap-3">
              {headers.map((h) => (
                <div key={h}>
                  <input
                    type="text"
                    className="px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                    placeholder={`Filter ${h}`}
                    value={filters[h] || ""}
                    onChange={(e) =>
                      setFilters((prev) => ({ ...prev, [h]: e.target.value }))
                    }
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Chart */}
      <div className="bg-gray-50 p-4 rounded-lg">{renderChart()}</div>

      {/* Data Info */}
      {csvData.length > 0 && (
        <div className="mt-4 text-sm text-gray-600">
          <p>
            Data rows: {filteredData.length} / {csvData.length}
          </p>
          <p>Headers: {headers.join(", ")}</p>
        </div>
      )}
    </div>
  );
};

export default CsvChartViewer;
