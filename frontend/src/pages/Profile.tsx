import React from "react";
import { useAuth } from "../context/AuthContext";

const Profile: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-hsbc-red to-hsbc-blue rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Profile</h1>
        <p className="text-white/80">Manage your account settings</p>
      </div>

      <div className="card-hsbc p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          User Information
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Name
            </label>
            <p className="text-gray-900 dark:text-white">
              {user?.displayName || "Not provided"}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Email
            </label>
            <p className="text-gray-900 dark:text-white">
              {user?.email || "Not provided"}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Role
            </label>
            <p className="text-gray-900 dark:text-white capitalize">
              {user?.role || "analyst"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
