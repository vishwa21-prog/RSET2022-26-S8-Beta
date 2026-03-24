import React, { useState, useEffect } from "react";
import { Activity, Users, FileText, Pill, Calendar } from "lucide-react";
import { supabase } from "./supabaseClient";

// Components
import TabButton from "./components/TabButton";

// Views
import DashboardView from "./views/dashboard/DashboardView";
import ConsentView from "./views/consent/ConsentView";
import DrugMatchingView from "./views/drugmatching/DrugMatchingView";
import EligibilityScreeningView from "./views/eligibilityscreening/EligibilityScreeningView";
import SchedulingView from "./views/scheduling/SchedulingView";

// Auth
import LandingPage from "./auth/LandingPage.jsx";
import Signup from "./auth/Signup";
import Login from "./auth/Login";

function App() {
  const [authMode, setAuthMode] = useState("landing"); // ✅ removed 96
  const [user, setUser] = useState(undefined);
  const [activeTab, setActiveTab] = useState("dashboard");

  // 🔐 Auth State
  useEffect(() => {
    const getSession = async () => {
      try {
        const { data, error } = await supabase.auth.getSession();

        if (error) {
          console.error("Session error:", error);
          setUser(null);
          return;
        }

        if (data?.session) {
          const authUser = data.session.user;

          const { data: profile, error: profileError } = await supabase
            .from("profiles")
            .select("role, patient_id")
            .eq("id", authUser.id)
            .maybeSingle();

          if (profileError || !profile) {
            console.error("Profile error:", profileError);
            setUser(null);
            return;
          }

          setUser(profile);
        } else {
          setUser(null);
        }
      } catch (err) {
        console.error("Unexpected auth error:", err);
        setUser(null);
      }
    };

    getSession();

    const { data: listener } = supabase.auth.onAuthStateChange(
      async (_event, session) => {
        if (session) {
          const { data: profile } = await supabase
            .from("profiles")
            .select("role, patient_id")
            .eq("id", session.user.id)
            .maybeSingle();

          setUser(profile || null);
        } else {
          setUser(null);
        }
      }
    );

    return () => {
      listener.subscription.unsubscribe();
    };
  }, []);

  // 🔒 LOGIN / LANDING CONTROL
  if (user === undefined) return <div>Loading...</div>;

  if (user === null) {
    if (authMode === "login") {
      return <Login onBack={() => setAuthMode("landing")} />;
    }

    if (authMode === "signup") {
      return <Signup onBack={() => setAuthMode("landing")} />;
    }

    return (
      <LandingPage
        onLogin={() => setAuthMode("login")}
        onSignup={() => setAuthMode("signup")}
      />
    );
  }

  // ✅ User is logged in
  const role = user.role;

  const roleTabs = {
    doctor: ["dashboard", "screening", "drugs", "scheduling"],
    patient: ["dashboard", "consent", "scheduling"],
    admin: ["dashboard", "screening", "consent", "drugs", "scheduling"],
  };

  const allowedTabs = roleTabs[role] || [];

  const renderContent = () => {
    if (!allowedTabs.includes(activeTab)) {
      return <DashboardView />;
    }

    switch (activeTab) {
      case "dashboard":
        return <DashboardView />;
      case "screening":
        return <EligibilityScreeningView />;
      case "consent":
        return <ConsentView currentUser={user} />;
      case "drugs":
        return <DrugMatchingView />;
      case "scheduling":
        return <SchedulingView />;
      default:
        return <DashboardView />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* HEADER */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Activity className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">
                ClinicSync AI
              </h1>
              <p className="text-sm text-gray-600">
                Clinical Trial Recruitment System
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              Logged in as: {user.patient_id} ({user.role})
            </span>

            <button
              onClick={async () => {
                await supabase.auth.signOut();
                setUser(null);
                setAuthMode("landing"); // ✅ reset auth mode
              }}
              className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* MAIN CONTENT */}
      <div className="max-w-7xl mx-auto px-6 py-6 grid grid-cols-5 gap-6">
        <div className="col-span-1 space-y-2">
          {allowedTabs.includes("dashboard") && (
            <TabButton
              id="dashboard"
              icon={Activity}
              label="Dashboard"
              activeTab={activeTab}
              onClick={setActiveTab}
            />
          )}

          {allowedTabs.includes("screening") && (
            <TabButton
              id="screening"
              icon={Users}
              label="Screening"
              activeTab={activeTab}
              onClick={setActiveTab}
            />
          )}

          {allowedTabs.includes("consent") && (
            <TabButton
              id="consent"
              icon={FileText}
              label="Consent"
              activeTab={activeTab}
              onClick={setActiveTab}
            />
          )}

          {allowedTabs.includes("drugs") && (
            <TabButton
              id="drugs"
              icon={Pill}
              label="Drugs"
              activeTab={activeTab}
              onClick={setActiveTab}
            />
          )}

          {allowedTabs.includes("scheduling") && (
            <TabButton
              id="scheduling"
              icon={Calendar}
              label="Scheduling"
              activeTab={activeTab}
              onClick={setActiveTab}
            />
          )}
        </div>

        <div className="col-span-4">{renderContent()}</div>
      </div>
    </div>
  );
}

export default App;