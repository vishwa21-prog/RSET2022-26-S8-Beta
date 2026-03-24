import React from "react";

const StatCard = ({ icon: Icon, label, value, color }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-2">
        <Icon className={`text-${color}-600`} size={24} />
        <span className={`text-2xl font-bold text-${color}-600`}>
          {value}
        </span>
      </div>
      <p className="text-sm text-gray-600">{label}</p>
    </div>
  );
};

export default StatCard;