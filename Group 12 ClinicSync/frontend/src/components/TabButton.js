import React from "react";

const TabButton = ({ id, icon: Icon, label, count, activeTab, onClick }) => {
  const isActive = activeTab === id;

  return (
    <button
      onClick={() => onClick(id)}
      className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg transition-all ${
        isActive
          ? "bg-blue-600 text-white shadow-lg"
          : "bg-white text-gray-700 hover:bg-gray-50"
      }`}
    >
      <Icon size={20} />
      <span className="flex-1 text-left font-medium">{label}</span>

      {count && (
        <span
          className={`px-2 py-1 rounded-full text-xs ${
            isActive ? "bg-blue-700" : "bg-gray-200"
          }`}
        >
          {count}
        </span>
      )}
    </button>
  );
};

export default TabButton;