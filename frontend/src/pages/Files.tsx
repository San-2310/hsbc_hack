import React from "react";

const Files: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-hsbc-red to-hsbc-blue rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Files</h1>
        <p className="text-white/80">Manage your uploaded data files</p>
      </div>

      <div className="card-hsbc p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Your Files
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          File management interface coming soon...
        </p>
      </div>
    </div>
  );
};

export default Files;
