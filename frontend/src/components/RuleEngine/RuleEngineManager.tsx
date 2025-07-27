import {
  AlertTriangle,
  CheckCircle,
  Download,
  Play,
  Plus,
  Settings,
  Trash2,
  Upload,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";

interface Rule {
  name: string;
  type: "normalization" | "aggregation" | "flag";
  config: any;
  created_at: string;
}

interface RuleEngineManagerProps {
  fileId?: string;
  onRulesApplied?: (results: any) => void;
}

const RuleEngineManager: React.FC<RuleEngineManagerProps> = ({
  fileId,
  onRulesApplied,
}) => {
  const [rules, setRules] = useState<{ [key: string]: Rule[] }>({
    normalization: [],
    aggregation: [],
    flag: [],
  });
  const [templates, setTemplates] = useState<any>({});
  const [selectedRules, setSelectedRules] = useState<{
    [key: string]: string[];
  }>({
    normalization: [],
    aggregation: [],
    flag: [],
  });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"rules" | "templates" | "apply">(
    "rules"
  );

  useEffect(() => {
    fetchRules();
    fetchTemplates();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await fetch("/api/rule-engine/rules", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      const data = await response.json();

      if (
        data.status === "success" &&
        data.data &&
        typeof data.data === "object"
      ) {
        // Ensure all 3 keys exist and default to array if not
        setRules({
          normalization: data.data.normalization || [],
          aggregation: data.data.aggregation || [],
          flag: data.data.flag || [],
        });
      } else {
        toast.error("Invalid rules format received");
        setRules({ normalization: [], aggregation: [], flag: [] });
      }
    } catch (error) {
      console.error("Error fetching rules:", error);
      toast.error("Failed to fetch rules");
      setRules({ normalization: [], aggregation: [], flag: [] });
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch("/api/rule-engine/templates", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      const data = await response.json();
      if (data.status === "success") {
        setTemplates(data.data);
      }
    } catch (error) {
      console.error("Error fetching templates:", error);
    }
  };

  const createRule = async (
    ruleType: string,
    ruleName: string,
    ruleConfig: any
  ) => {
    try {
      const response = await fetch(`/api/rule-engine/${ruleType}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          rule_name: ruleName,
          rule_config: ruleConfig,
        }),
      });
      const data = await response.json();
      if (data.status === "success") {
        toast.success(`Rule '${ruleName}' created successfully`);
        fetchRules();
      } else {
        toast.error(data.message);
      }
    } catch (error) {
      toast.error("Failed to create rule");
    }
  };

  const deleteRule = async (ruleType: string, ruleName: string) => {
    try {
      const response = await fetch(
        `/api/rule-engine/rules/${ruleType}/${ruleName}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      const data = await response.json();
      if (data.status === "success") {
        toast.success(`Rule '${ruleName}' deleted successfully`);
        fetchRules();
      } else {
        toast.error(data.message);
      }
    } catch (error) {
      toast.error("Failed to delete rule");
    }
  };

  const applyRules = async () => {
    if (!fileId) {
      toast.error("No file selected");
      return;
    }

    setLoading(true);
    try {
      const ruleTypes = Object.keys(selectedRules).filter(
        (key) => selectedRules[key].length > 0
      );
      const ruleNames = Object.fromEntries(
        Object.entries(selectedRules).filter(([_, rules]) => rules.length > 0)
      );

      const response = await fetch("/api/rule-engine/apply", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          file_id: fileId,
          rule_types: ruleTypes,
          rule_names: ruleNames,
        }),
      });
      const data = await response.json();
      if (data.status === "success") {
        toast.success("Rules applied successfully");
        onRulesApplied?.(data.data);
      } else {
        toast.error(data.message);
      }
    } catch (error) {
      toast.error("Failed to apply rules");
    } finally {
      setLoading(false);
    }
  };

  const exportRules = async () => {
    try {
      const response = await fetch("/api/rule-engine/export", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      const data = await response.json();
      if (data.status === "success") {
        const blob = new Blob([JSON.stringify(data.data.rules, null, 2)], {
          type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "hsbc-rules.json";
        a.click();
        URL.revokeObjectURL(url);
        toast.success("Rules exported successfully");
      }
    } catch (error) {
      toast.error("Failed to export rules");
    }
  };

  const importRules = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const rulesData = JSON.parse(text);

      const response = await fetch("/api/rule-engine/import", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          rules_json: JSON.stringify(rulesData),
        }),
      });
      const data = await response.json();
      if (data.status === "success") {
        toast.success("Rules imported successfully");
        fetchRules();
      } else {
        toast.error(data.message);
      }
    } catch (error) {
      toast.error("Failed to import rules");
    }
  };

  const toggleRuleSelection = (ruleType: string, ruleName: string) => {
    const key = ruleType.toLowerCase();
    setSelectedRules((prev) => ({
      ...prev,
      [key]: prev[key]?.includes(ruleName)
        ? prev[key].filter((name) => name !== ruleName)
        : [...(prev[key] || []), ruleName],
    }));
  };

  const addTemplateRule = (
    ruleType: string,
    templateName: string,
    templateConfig: any
  ) => {
    const ruleName = `${templateName}_${Date.now()}`;
    createRule(ruleType, ruleName, templateConfig);
  };

  const renderRuleCard = (rule: Rule, ruleType: string) => (
    <div
      key={rule.name}
      className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border"
    >
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-gray-900 dark:text-white">
          {rule.name}
        </h4>
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={selectedRules[ruleType].includes(rule.name)}
            onChange={() => toggleRuleSelection(ruleType, rule.name)}
            className="rounded border-gray-300"
          />
          <button
            onClick={() => deleteRule(ruleType, rule.name)}
            className="text-red-500 hover:text-red-700"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
      <div className="text-sm text-gray-600 dark:text-gray-400">
        <div>Type: {rule.type}</div>
        <div>Created: {new Date(rule.created_at).toLocaleDateString()}</div>
      </div>
    </div>
  );

  const renderTemplateCard = (
    templateName: string,
    templateConfig: any,
    ruleType: string
  ) => (
    <div
      key={templateName}
      className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border"
    >
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-gray-900 dark:text-white">
          {templateName}
        </h4>
        <button
          onClick={() =>
            addTemplateRule(ruleType, templateName, templateConfig)
          }
          className="text-blue-500 hover:text-blue-700"
        >
          <Plus size={16} />
        </button>
      </div>
      <div className="text-sm text-gray-600 dark:text-gray-400">
        <div>Type: {templateConfig.type}</div>
        <div>Description: {templateConfig.description || "No description"}</div>
      </div>
    </div>
  );

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg">
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex space-x-8 px-6">
          <button
            onClick={() => setActiveTab("rules")}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === "rules"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <Settings className="inline mr-2" size={16} />
            Rules
          </button>
          <button
            onClick={() => setActiveTab("templates")}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === "templates"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <Download className="inline mr-2" size={16} />
            Templates
          </button>
          <button
            onClick={() => setActiveTab("apply")}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === "apply"
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <Play className="inline mr-2" size={16} />
            Apply Rules
          </button>
        </nav>
      </div>

      <div className="p-6">
        {activeTab === "rules" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Rule Management
              </h3>
              <div className="flex space-x-2">
                <button
                  onClick={exportRules}
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  <Download size={16} className="mr-2" />
                  Export
                </button>
                <label className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 cursor-pointer">
                  <Upload size={16} className="mr-2" />
                  Import
                  <input
                    type="file"
                    accept=".json"
                    onChange={importRules}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {Object.entries(rules).map(([ruleType, ruleList]) => {
              if (!Array.isArray(ruleList)) {
                console.warn(
                  `Expected ruleList to be an array for ${ruleType}, but got:`,
                  ruleList
                );
                return null;
              }

              return (
                <div key={ruleType} className="space-y-4">
                  <h4 className="text-md font-medium text-gray-900 dark:text-white capitalize">
                    {ruleType} Rules ({ruleList.length})
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* {ruleList.map((rule) => renderRuleCard(rule, ruleType))} */}
                    {ruleList.map((rule) =>
                      renderRuleCard(rule, ruleType.toLowerCase())
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {activeTab === "templates" && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Rule Templates
            </h3>
            {Object.entries(templates).map(
              ([ruleType, templateList]: [string, any]) => (
                <div key={ruleType} className="space-y-4">
                  <h4 className="text-md font-medium text-gray-900 dark:text-white capitalize">
                    {ruleType} Templates
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(templateList).map(
                      ([templateName, templateConfig]: [string, any]) =>
                        renderTemplateCard(
                          templateName,
                          templateConfig,
                          ruleType
                        )
                    )}
                  </div>
                </div>
              )
            )}
          </div>
        )}

        {activeTab === "apply" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Apply Rules
              </h3>
              <button
                onClick={applyRules}
                disabled={loading || !fileId}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                ) : (
                  <Play size={16} className="mr-2" />
                )}
                Apply Selected Rules
              </button>
            </div>

            {!fileId && (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-4">
                <div className="flex">
                  <AlertTriangle className="text-yellow-400 mr-2" size={20} />
                  <div className="text-yellow-800 dark:text-yellow-200">
                    No file selected. Please upload a file first to apply rules.
                  </div>
                </div>
              </div>
            )}

            {Object.entries(selectedRules).map(
              ([ruleType, selectedRuleList]) => (
                <div key={ruleType} className="space-y-4">
                  <h4 className="text-md font-medium text-gray-900 dark:text-white capitalize">
                    Selected {ruleType} Rules ({selectedRuleList.length})
                  </h4>
                  {selectedRuleList.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {selectedRuleList.map((ruleName) => (
                        <div
                          key={ruleName}
                          className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-3"
                        >
                          <div className="flex items-center">
                            <CheckCircle
                              className="text-green-500 mr-2"
                              size={16}
                            />
                            <span className="text-green-800 dark:text-green-200">
                              {ruleName}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-gray-500 dark:text-gray-400 text-sm">
                      No {ruleType} rules selected
                    </div>
                  )}
                </div>
              )
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RuleEngineManager;
