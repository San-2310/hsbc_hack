import React from "react";
import { Link, useLocation } from "react-router-dom";

const Sidebar: React.FC = () => {
  const location = useLocation();

  const navigation = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: "📊",
    },
    {
      name: "Upload",
      href: "/upload",
      icon: "📁",
    },
    {
      name: "Files",
      href: "/files",
      icon: "📋",
    },
    {
      name: "Processing",
      href: "/processing",
      icon: "⚙️",
    },
    {
      name: "Analytics",
      href: "/analytics",
      icon: "📈",
    },
    {
      name: "Profile",
      href: "/profile",
      icon: "👤",
    },
  ];

  return (
    <div className="w-64 bg-white dark:bg-gray-800 shadow-lg border-r border-gray-200 dark:border-gray-700">
      <div className="p-6">
        <div className="flex items-center space-x-2 mb-8">
          <div className="w-8 h-8 bg-hsbc-red rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">H</span>
          </div>
          <span className="text-lg font-semibold text-gray-900 dark:text-white">
            HSBC
          </span>
        </div>

        <nav className="space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`sidebar-item ${isActive ? "active" : ""}`}
              >
                <span className="mr-3">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default Sidebar;
