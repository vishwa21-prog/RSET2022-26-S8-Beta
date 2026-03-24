import { useEffect, useState } from "react";
import { supabase } from "../../supabaseClient";

export const useDashboardLogic = () => {
  const [stats, setStats] = useState({
    totalPatients: 0,
    eligible: 0,
    screened: 0,
    enrolled: 0,
  });

  const [recentPatients, setRecentPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // const fetchDashboardData = async () => {
    //   try {
    //     setLoading(true);

    //     // 🔹 Fetch patients from Supabase (replace table name if needed)
    //     const { data, error } = await supabase
    //       .from("patients")
    //       .select("*")
    //       .order("created_at", { ascending: false })
    //       .limit(10);

    //     if (error) throw error;

    //     // 🔹 Compute stats dynamically
    //     const totalPatients = data.length;
    //     const eligible = data.filter(p => p.status === "eligible").length;
    //     const screened = data.filter(p => p.status === "screening").length;
    //     const enrolled = data.filter(p => p.status === "enrolled").length;

    //     setStats({
    //       totalPatients,
    //       eligible,
    //       screened,
    //       enrolled,
    //     });

    //     setRecentPatients(data);
    //   } catch (err) {
    //     console.error("Dashboard fetch error:", err);
    //   } finally {
    //     setLoading(false);
    //   }
    // };

    // fetchDashboardData();
  }, []);

  return {
    stats,
    recentPatients,
    loading,
  };
};