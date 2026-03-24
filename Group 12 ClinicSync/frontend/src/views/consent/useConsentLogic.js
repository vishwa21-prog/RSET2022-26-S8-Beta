import { useState, useEffect } from "react";

export const useConsentLogic = (currentUser) => {
  const [selectedPatient, setSelectedPatient] = useState("");
  const [language, setLanguage] = useState("english");
  const [consentGenerated, setConsentGenerated] = useState(false);
  const [selectedPatientData, setSelectedPatientData] = useState(null);
  const [decision, setDecision] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const role = currentUser?.role;

  // 🔹 Simulated patients
  const patients = [
    { id: "P001", age: 52, sex: "M" },
    { id: "P002", age: 45, sex: "F" },
    { id: "P003", age: 58, sex: "M" },
    { id: "P004", age: 41, sex: "F" },
  ];

  const effectivePatientId =
    role === "patient" ? currentUser?.patient_id : selectedPatient;

  // 🔹 Auto-load patient data
  useEffect(() => {
    if (!effectivePatientId) {
      setSelectedPatientData(null);
      return;
    }

    const patient = patients.find(
      (p) => p.id === effectivePatientId
    );

    setSelectedPatientData(patient || null);
  }, [effectivePatientId]);

  // 🔥 Generate Consent
  const handleGenerateConsent = async ({ notes, complexity }) => {
    if (!effectivePatientId) {
      alert("Please select a patient");
      return null;
    }

    try {
      const response = await fetch(
        "http://localhost:5000/consent/generate",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            patient_id: effectivePatientId,
            language,
            literacy_level: complexity,
            consent_type: complexity,
            notes,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to generate consent");
      }

      setConsentGenerated(true);
      return data;

    } catch (error) {
      console.error(error);
      alert("Error generating consent.");
      return null;
    }
  };

  // 🔹 Upload Signed Consent
  const handleUploadSigned = async () => {
    if (!selectedFile) {
      alert("Please upload signed consent file");
      return;
    }

    if (!effectivePatientId) {
      alert("No patient selected");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("patient_id", effectivePatientId);
      formData.append("file", selectedFile);

      const response = await fetch(
        "http://localhost:5000/consent/upload-signed",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      console.log("Signed upload response:", data);
      alert("Signed consent uploaded successfully!");

    } catch (error) {
      console.error(error);
      alert("Error uploading signed consent.");
    }
  };

  // 🔹 Decline Consent
  const handleDecline = async () => {
    if (!effectivePatientId) {
      alert("No patient selected");
      return;
    }

    try {
      await fetch(
        `http://localhost:5000/consent/decline/${effectivePatientId}`,
        {
          method: "POST",
        }
      );

      alert("Consent declined.");

    } catch (error) {
      console.error(error);
      alert("Error declining consent.");
    }
  };

  // 🔹 Consent Templates (Preview Only)
  const consentTemplates = {
    english: {
      title: "INFORMED CONSENT FORM",
      subtitle: "Clinical Trial for Type 2 Diabetes Treatment",
      sections: [
        {
          heading: "Purpose of the Study",
          content:
            "You are invited to participate in a study evaluating treatment options for Type 2 Diabetes.",
        },
        {
          heading: "Study Duration",
          content:
            "Participation lasts approximately 6 months with regular follow-ups.",
        },
        {
          heading: "Risks",
          content:
            "Possible risks include nausea, dizziness, and minor discomfort.",
        },
        {
          heading: "Confidentiality",
          content:
            "All personal and medical information will remain confidential.",
        },
      ],
    },
    hindi: {
      title: "सूचित सहमति पत्र",
      subtitle: "टाइप 2 मधुमेह उपचार परीक्षण",
      sections: [
        {
          heading: "अध्ययन का उद्देश्य",
          content:
            "आपको टाइप 2 मधुमेह के उपचार परीक्षण में भाग लेने के लिए आमंत्रित किया जाता है।",
        },
      ],
    },
    malayalam: {
      title: "അറിവുള്ള സമ്മത ഫോം",
      subtitle: "ടൈപ്പ് 2 പ്രമേഹ ചികിത്സാ പരീക്ഷണം",
      sections: [
        {
          heading: "പഠനത്തിന്റെ ഉദ്ദേശ്യം",
          content:
            "ടൈപ്പ് 2 പ്രമേഹ ചികിത്സാ പരീക്ഷണത്തിൽ പങ്കെടുക്കാൻ നിങ്ങളെ ക്ഷണിക്കുന്നു.",
        },
      ],
    },
  };

  return {
    selectedPatient,
    setSelectedPatient,
    language,
    setLanguage,
    consentGenerated,
    patients,
    consentTemplates,
    selectedPatientData,
    handleGenerateConsent,
    decision,
    setDecision,
    selectedFile,
    setSelectedFile,
    handleUploadSigned,
    handleDecline,
  };
};