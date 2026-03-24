import React from "react";
import { Pill } from "lucide-react";
import { useDrugMatchingLogic } from "./useDrugMatchingLogic";

const DrugMatchingView = () => {
  const {
    step,
    setStep,
    file,
    loading,
    drugSchema,
    handleFileUpload,
    downloadTemplate,
    handleDrugMatching,
  } = useDrugMatchingLogic();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">
        Drug Matching
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

      {/* STEP 1 - Schema */}
      {step === 1 && (
        <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
          <h3 className="text-lg font-semibold">
            Input File Requirements
          </h3>

          <table className="w-full border text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left">Parameter</th>
                <th className="px-4 py-2 text-left">Description</th>
                <th className="px-4 py-2 text-left">Example</th>
              </tr>
            </thead>
            <tbody>
              {drugSchema.map((row) => (
                <tr key={row.param} className="border-t">
                  <td className="px-4 py-2 font-mono">{row.param}</td>
                  <td className="px-4 py-2">{row.description}</td>
                  <td className="px-4 py-2 text-gray-600">{row.example}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <button
            onClick={downloadTemplate}
            className="bg-white border px-4 py-2 rounded-lg text-sm hover:bg-gray-50"
          >
            Download Sample Template
          </button>
        </div>
      )}

      {/* STEP 2 - Upload */}
      {step === 2 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">
            Upload Eligible Patient Data
          </h3>

          <input
            type="file"
            accept=".csv,.xlsx"
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

      {/* STEP 3 - Run */}
      {step === 3 && (
        <div className="bg-white rounded-xl shadow-sm p-6 text-center">
          <h3 className="text-lg font-semibold mb-4">
            Run Drug Matching Algorithm
          </h3>

          <button
            onClick={handleDrugMatching}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-blue-700 disabled:bg-gray-400"
          >
            <Pill size={20} />
            {loading ? "Processing..." : "Run Drug Matching"}
          </button>
        </div>
      )}
    </div>
  );
};

export default DrugMatchingView;