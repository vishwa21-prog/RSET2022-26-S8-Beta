import { useState } from "react";

export const useEligibilityScreeningLogic = () => {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const csvSchema = [
    {
      param: "patient_id",
      description: "Unique patient identifier",
      unit: "-",
      example: "P001",
    },
    {
      param: "age",
      description: "Patient age",
      unit: "Years",
      example: "45",
    },
    {
      param: "glucose",
      description: "Fasting blood glucose level",
      unit: "mg/dL",
      example: "180",
    },
    {
      param: "hba1c",
      description: "HbA1c value",
      unit: "%",
      example: "7.8",
    },
    {
      param: "bmi",
      description: "Body Mass Index",
      unit: "kg/m²",
      example: "29.4",
    },
  ];

  const handleFileUpload = (e) => {
    setFile(e.target.files[0]);
  };

  const downloadTemplate = () => {
    const csvContent =
      "patient_id,age,glucose,hba1c,bmi\n" +
      "P001,52,187,8.2,31.4\n" +
      "P002,45,145,7.1,27.6\n";

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "eligibility_sample_template.csv";
    a.click();

    window.URL.revokeObjectURL(url);
  };

  const handleEligibilityCheck = async () => {
    if (!file) {
      alert("Please upload the patient CSV file first.");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Eligibility screening failed");
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "eligible_patients_with_id.csv";
      a.click();

      window.URL.revokeObjectURL(url);

      alert("Eligibility screening completed successfully!");
    } catch (error) {
      console.error(error);
      alert("Error running eligibility screening.");
    } finally {
      setLoading(false);
    }
  };

  return {
    step,
    setStep,
    file,
    loading,
    csvSchema,
    handleFileUpload,
    downloadTemplate,
    handleEligibilityCheck,
  };
};