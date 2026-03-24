import React from "react";
import { Calendar, CheckCircle, Clock } from "lucide-react";
import { useSchedulingLogic } from "./useSchedulingLogic";

const SchedulingView = () => {
  const {
    appointments,
    formData,
    handleInputChange,
    handleAddAppointment,
    handleStatusChange,
  } = useSchedulingLogic();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">
        Appointment Scheduling
      </h2>

      {/* Appointment Form */}
      <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
        <h3 className="text-lg font-semibold">Schedule New Appointment</h3>

        <input
          type="text"
          name="patientId"
          placeholder="Patient ID"
          value={formData.patientId}
          onChange={handleInputChange}
          className="w-full px-4 py-2 border rounded-lg"
        />

        <input
          type="text"
          name="doctor"
          placeholder="Doctor Name"
          value={formData.doctor}
          onChange={handleInputChange}
          className="w-full px-4 py-2 border rounded-lg"
        />

        <input
          type="date"
          name="date"
          value={formData.date}
          onChange={handleInputChange}
          className="w-full px-4 py-2 border rounded-lg"
        />

        <input
          type="time"
          name="time"
          value={formData.time}
          onChange={handleInputChange}
          className="w-full px-4 py-2 border rounded-lg"
        />

        <button
          onClick={handleAddAppointment}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Calendar size={20} />
          Schedule Appointment
        </button>
      </div>

      {/* Appointment List */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">
          Upcoming Appointments
        </h3>

        <table className="w-full text-sm">
          <thead className="border-b">
            <tr>
              <th className="text-left py-2">Patient</th>
              <th className="text-left py-2">Doctor</th>
              <th className="text-left py-2">Date</th>
              <th className="text-left py-2">Time</th>
              <th className="text-left py-2">Status</th>
              <th className="text-left py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {appointments.map((appt) => (
              <tr key={appt.id} className="border-b">
                <td className="py-2">{appt.patientId}</td>
                <td className="py-2">{appt.doctor}</td>
                <td className="py-2">{appt.date}</td>
                <td className="py-2">{appt.time}</td>
                <td className="py-2">
                  <span
                    className={`px-2 py-1 rounded-full text-xs font-medium ${
                      appt.status === "confirmed"
                        ? "bg-green-100 text-green-700"
                        : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {appt.status}
                  </span>
                </td>
                <td className="py-2">
                  {appt.status === "pending" && (
                    <button
                      onClick={() =>
                        handleStatusChange(appt.id, "confirmed")
                      }
                      className="text-blue-600 flex items-center gap-1"
                    >
                      <CheckCircle size={14} />
                      Confirm
                    </button>
                  )}
                  {appt.status === "confirmed" && (
                    <span className="text-gray-500 flex items-center gap-1">
                      <Clock size={14} />
                      Scheduled
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SchedulingView;