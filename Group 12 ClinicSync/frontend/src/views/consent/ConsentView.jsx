import React, { useState } from "react";
import { FileText, CheckCircle } from "lucide-react";
import { useConsentLogic } from "./useConsentLogic";

const ConsentView = ({ currentUser }) => {
  const {
  selectedPatient,
  setSelectedPatient,
  language,
  setLanguage,
  consentGenerated,
  patients,
  consentTemplates,
  selectedPatientData,
  handleGenerateConsent,   // ✅ ADD THIS LINE
  decision,
  setDecision,
  selectedFile,
  setSelectedFile,
  handleUploadSigned,
  handleDecline,
} = useConsentLogic(currentUser);

  const role = currentUser?.role;
  const patientId = currentUser?.patient_id;

  const [notes, setNotes] = useState("");
  const [complexity, setComplexity] = useState("simple");
  const [uploadedImage, setUploadedImage] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null); // ✅ NEW

  const currentContent = consentTemplates[language];

  const handleGenerate = async () => {
    const response = await handleGenerateConsent({
      notes,
      complexity,
      uploadedImage,
    });

    if (response?.download_url) {
      setDownloadUrl(response.download_url); // ✅ STORE URL
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">
        Consent Form Generation
      </h2>

      <div className="bg-white rounded-xl shadow-sm p-6 space-y-6">

        {/* Doctor/Admin Patient Selection */}
        {role !== "patient" && (
          <select
            value={selectedPatient}
            onChange={(e) => setSelectedPatient(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg"
          >
            <option value="">-- Select Patient --</option>
            {patients.map((p) => (
              <option key={p.id} value={p.id}>
                {p.id} - Age {p.age}
              </option>
            ))}
          </select>
        )}

        {/* Patient Auto ID */}
        {role === "patient" && (
          <div className="bg-blue-50 p-3 rounded-lg text-sm">
            <strong>Patient ID:</strong> {patientId}
          </div>
        )}

        {/* Language */}
        <div className="flex gap-3">
          {["english", "hindi", "malayalam"].map((lang) => (
            <button
              key={lang}
              onClick={() => setLanguage(lang)}
              className={`px-4 py-2 rounded-lg ${
                language === lang
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200"
              }`}
            >
              {lang}
            </button>
          ))}
        </div>

        {/* Consent Type */}
        <div>
          <label className="block font-semibold mb-2">
            Consent Type
          </label>
          <div className="flex gap-4">
            <button
              onClick={() => setComplexity("simple")}
              className={`px-4 py-2 rounded-lg ${
                complexity === "simple"
                  ? "bg-green-600 text-white"
                  : "bg-gray-200"
              }`}
            >
              Simple
            </button>

            <button
              onClick={() => setComplexity("technical")}
              className={`px-4 py-2 rounded-lg ${
                complexity === "technical"
                  ? "bg-purple-600 text-white"
                  : "bg-gray-200"
              }`}
            >
              Technical
            </button>
          </div>
        </div>

        {/* Notes */}
        <div>
          <label className="block font-semibold mb-2">
            Additional Clinical Notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full border rounded-lg px-4 py-2 h-28 resize-none"
          />
        </div>

        {/* Image Upload */}
        <div>
          <label className="block font-semibold mb-2">
            Upload Supporting Document
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setUploadedImage(e.target.files[0])}
            className="w-full border rounded-lg px-3 py-2"
          />
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <FileText size={22} />
          Generate Consent
        </button>

        {/* ✅ SHOW DOWNLOAD BUTTON AFTER GENERATION */}
        {downloadUrl && (
          <a
            href={downloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-purple-600 text-white px-6 py-3 rounded-lg inline-block text-center hover:bg-purple-700"
          >
            Download Generated Consent PDF
          </a>
        )}

        {/* Upload Signed Consent */}
{role === "patient" && (
  <div>
    <label className="block font-semibold mb-2">
      Upload Signed Consent
    </label>

    <input
      type="file"
      accept=".pdf"
      onChange={(e) => setSelectedFile(e.target.files[0])}   // ✅ CONNECT FILE
      className="w-full border rounded-lg px-2 py-2"
    />

    <button
      onClick={handleUploadSigned}   // ✅ CONNECT BUTTON
      className="mt-3 bg-green-600 text-white py-3 rounded-lg w-full hover:bg-green-700 transition"
    >
      Submit Signed Consent
    </button>
  </div>
)}
      </div>
    </div>
  );
};

export default ConsentView;