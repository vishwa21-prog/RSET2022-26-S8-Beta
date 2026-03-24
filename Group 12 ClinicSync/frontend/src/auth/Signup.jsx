import React, { useState } from "react";
import { supabase } from "../supabaseClient";

const Signup = ({ onBack }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("patient");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      // 1️⃣ Create user in Supabase Auth
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      });

      if (error) {
        setErrorMsg(error.message);
        setLoading(false);
        return;
      }

      if (!data.user) {
        setErrorMsg("User creation failed.");
        setLoading(false);
        return;
      }

      // 2️⃣ Insert into profiles table
      const { error: profileError } = await supabase
        .from("profiles")
        .insert([
          {
            id: data.user.id,
            role: role,
            patient_id: email,
          },
        ]);

      if (profileError) {
        console.error("Profile insert error:", profileError);
        setErrorMsg("Profile creation failed.");
        setLoading(false);
        return;
      }

      // 3️⃣ Auto-login after signup
      const { error: loginError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (loginError) {
        setErrorMsg(loginError.message);
        setLoading(false);
        return;
      }

      // No navigation needed
      // App.js auth listener will automatically show dashboard

      setLoading(false);
    } catch (err) {
      console.error("Unexpected signup error:", err);
      setErrorMsg("Something went wrong.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-blue-900 px-4">
      <div className="bg-white p-8 rounded-xl shadow-xl w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-blue-900">
          Create Account
        </h2>

        {errorMsg && (
          <p className="text-red-500 text-sm mb-4 text-center">
            {errorMsg}
          </p>
        )}

        <form onSubmit={handleSignup} className="flex flex-col gap-4">

          <input
            type="email"
            placeholder="Email"
            className="border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            className="border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <select
            className="border p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="patient">Patient</option>
            <option value="doctor">Doctor</option>
            <option value="admin">Admin</option>
          </select>

          <button
            type="submit"
            disabled={loading}
            className="bg-blue-900 text-white py-3 rounded-lg hover:bg-blue-800 transition"
          >
            {loading ? "Creating Account..." : "Sign Up"}
          </button>
        </form>

        <button
          onClick={onBack}
          className="mt-5 text-sm text-gray-600 hover:underline w-full text-center"
        >
          ← Back
        </button>
      </div>
    </div>
  );
};

export default Signup