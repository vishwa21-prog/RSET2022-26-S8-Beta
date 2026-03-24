
import { useState } from "react";

export const useSchedulingLogic = () => {
  const [appointments, setAppointments] = useState([
    {
      id: 1,
      patientId: "P001",
      doctor: "Dr. Sharma",
      date: "2026-03-01",
      time: "10:00 AM",
      status: "confirmed",
    },
    {
      id: 2,
      patientId: "P002",
      doctor: "Dr. Nair",
      date: "2026-03-02",
      time: "11:30 AM",
      status: "pending",
    },
  ]);

  const [formData, setFormData] = useState({
    patientId: "",
    doctor: "",
    date: "",
    time: "",
  });

  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleAddAppointment = () => {
    if (!formData.patientId || !formData.date || !formData.time) {
      alert("Please fill all required fields.");
      return;
    }

    const newAppointment = {
      id: Date.now(),
      ...formData,
      status: "confirmed",
    };

    setAppointments([...appointments, newAppointment]);

    setFormData({
      patientId: "",
      doctor: "",
      date: "",
      time: "",
    });

    alert("Appointment scheduled successfully!");
  };

  const handleStatusChange = (id, newStatus) => {
    const updated = appointments.map((appt) =>
      appt.id === id ? { ...appt, status: newStatus } : appt
    );

    setAppointments(updated);
  };

  return {
    appointments,
    formData,
    loading,
    handleInputChange,
    handleAddAppointment,
    handleStatusChange,
  };
};