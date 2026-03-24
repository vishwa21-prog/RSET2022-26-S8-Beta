import React from "react";
import { CheckCircle } from "lucide-react";
import { useEligibilityScreeningLogic } from "./useEligibilityScreeningLogic";

const EligibilityScreeningView = () => {
  const {
    step,
    setStep,
    file,
    loading,
    csvSchema,
    handleFileUpload,
    downloadTemplate,
    handleEligibilityCheck,
  } = useEligibilityScreeningLogic();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">
        Eligibility Screening
      </h2>

      {/* Step Navigation */}
      <div className="flex gap-4">
        {[1, 2, 3].map((s) => (
          <button
            key={s}
            onClick={() => setStep(s)}
            className={`px-4 py-2 rounded-lg text-sm font-medium ${
              step === s
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700"
            }`}
          >
            Step {s}
          </button>
        ))}
      </div>

      {/* STEP 1 - Template Preview */}
      {step === 1 && (
        <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
          <h3 className="text-lg font-semibold">
            Sample CSV Template
          </h3>

          <table className="w-full border text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left">Parameter</th>
                <th className="px-4 py-2 text-left">Description</th>
                <th className="px-4 py-2 text-left">Unit</th>
                <th className="px-4 py-2 text-left">Example</th>
              </tr>
            </thead>
            <tbody>
              {csvSchema.map((row) => (
                <tr key={row.param} className="border-t">
                  <td className="px-4 py-2 font-mono">{row.param}</td>
                  <td className="px-4 py-2">{row.description}</td>
                  <td className="px-4 py-2">{row.unit}</td>
                  <td className="px-4 py-2 text-gray-600">
                    {row.example}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <button
            onClick={downloadTemplate}
            className="bg-white border px-4 py-2 rounded-lg text-sm hover:bg-gray-50"
          >
            Download Sample CSV Template
          </button>
        </div>
      )}

      {/* STEP 2 - Upload */}
      {step === 2 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">
            Upload Patient Data (CSV)
          </h3>

          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            className="block w-full text-sm"
          />

          {file && (
            <p className="mt-3 text-sm text-green-600">
              Uploaded file: {file.name}
            </p>
          )}
        </div>
      )}

      {/* STEP 3 - Run Screening */}
      {step === 3 && (
        <div className="bg-white rounded-xl shadow-sm p-6 text-center">
          <h3 className="text-lg font-semibold mb-4">
            Run Eligibility Screening
          </h3>

          <button
            onClick={handleEligibilityCheck}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-blue-700 disabled:bg-gray-400"
          >
            <CheckCircle size={20} />
            {loading ? "Processing..." : "Check Eligibility"}
          </button>
        </div>
      )}
    </div>
  );
};

export default EligibilityScreeningView;