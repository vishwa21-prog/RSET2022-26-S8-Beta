import React from "react";
import { Users, CheckCircle, Clock, Activity } from "lucide-react";
import { useDashboardLogic } from "./useDashboardLogic";
import StatCard from "../../components/StatCard";

const DashboardView = () => {
  const { stats, recentPatients, loading } = useDashboardLogic();

  if (loading) {
    return <div className="text-gray-600">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard icon={Users} label="Total Patients" value={stats.totalPatients} color="blue" />
        <StatCard icon={CheckCircle} label="Eligible" value={stats.eligible} color="green" />
        <StatCard icon={Clock} label="Screening" value={stats.screened} color="yellow" />
        <StatCard icon={Activity} label="Enrolled" value={stats.enrolled} color="purple" />
      </div>

      {/* Patient Table */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Recent Patient Screenings
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 text-sm text-gray-600">
                <th className="py-3 px-4 text-left">Patient ID</th>
                <th className="py-3 px-4 text-left">Age</th>
                <th className="py-3 px-4 text-left">Glucose</th>
                <th className="py-3 px-4 text-left">HbA1c</th>
                <th className="py-3 px-4 text-left">Status</th>
              </tr>
            </thead>

            <tbody>
              {recentPatients.map(patient => (
                <tr key={patient.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4 text-blue-600 font-medium">
                    {patient.patient_id}
                  </td>
                  <td className="py-3 px-4">{patient.age}</td>
                  <td className="py-3 px-4">{patient.glucose} mg/dL</td>
                  <td className="py-3 px-4">{patient.hba1c}%</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      patient.status === "eligible"
                        ? "bg-green-100 text-green-700"
                        : patient.status === "screening"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-gray-100 text-gray-700"
                    }`}>
                      {patient.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>

          </table>
        </div>
      </div>

    </div>
  );
};

export default DashboardView;