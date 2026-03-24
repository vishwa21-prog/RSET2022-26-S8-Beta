import { useState } from "react";

export const useDrugMatchingLogic = () => {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const drugSchema = [
    { param: "patient_id", description: "Unique patient identifier", example: "P001" },
    { param: "age", description: "Patient age", example: "52" },
    { param: "hba1c", description: "HbA1c value", example: "8.1" },
    { param: "bmi", description: "Body Mass Index", example: "31.4" },
    { param: "egfr", description: "Kidney function (optional)", example: "85" },
  ];

  const handleFileUpload = (e) => {
    setFile(e.target.files[0]);
  };

  const downloadTemplate = () => {
    const csv =
      "patient_id,age,hba1c,bmi,egfr\n" +
      "P001,52,8.2,31.4,85\n";

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "drug_matching_input_template.csv";
    a.click();

    window.URL.revokeObjectURL(url);
  };

  const handleDrugMatching = async () => {
    if (!file) {
      alert("Please upload the eligible patients file first.");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:5000/drug-matching", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Drug matching failed");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "drug_matching_results.xlsx";
      a.click();

      window.URL.revokeObjectURL(url);

      alert("Drug matching completed successfully!");
    } catch (error) {
      console.error(error);
      alert("Error running drug matching.");
    } finally {
      setLoading(false);
    }
  };

  return {
    step,
    setStep,
    file,
    loading,
    drugSchema,
    handleFileUpload,
    downloadTemplate,
    handleDrugMatching,
  };
};