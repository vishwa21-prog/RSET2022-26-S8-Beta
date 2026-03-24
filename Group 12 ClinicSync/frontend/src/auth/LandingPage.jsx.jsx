import React from "react";

const LandingPage = ({ onLogin, onSignup }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-blue-700 to-blue-500 flex items-center justify-center px-4">
      
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-10 max-w-lg w-full text-center text-white border border-white/20">
        
        {/* Logo / Title */}
        <h1 className="text-4xl font-bold mb-3 tracking-wide">
          ClinicSync AI
        </h1>

        <p className="text-sm text-blue-100 mb-6">
          Intelligent Clinical Trial Recruitment Platform
        </p>

        {/* Divider */}
        <div className="w-16 h-1 bg-white mx-auto mb-6 rounded-full"></div>

        {/* Question */}
        <h2 className="text-base font-medium mb-2 text-blue-100">
          Are you a new user?
        </h2>

        <p className="text-blue-100 mb-8">
          Create an account to get started, or log in if you already have one.
        </p>

        {/* Buttons */}
        <div className="flex flex-col gap-4">
          <button
            onClick={onSignup || onLogin}
            className="bg-white text-blue-900 font-semibold py-3 rounded-lg hover:bg-gray-200 transition duration-300"
          >
            Sign Up
          </button>

          <button
            onClick={onLogin}
            className="border border-white py-3 rounded-lg hover:bg-white hover:text-blue-900 transition duration-300"
          >
            Login
          </button>
        </div>

        {/* Footer */}
        <p className="text-xs text-blue-200 mt-8">
          © 2026 ClinicSync AI | Secure Clinical Data Platform
        </p>
      </div>
    </div>
  );
};

export default LandingPage;