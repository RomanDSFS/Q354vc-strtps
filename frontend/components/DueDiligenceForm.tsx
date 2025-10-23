"use client";
import React, { useState } from "react";

const questions = [
  {
    category: "1. Problem and Its Relevance",
    items: [
      {
        question: "Percentage of target audience facing the problem",
        options: ["<1%", "1-10%", "11-50%", ">50%"],
      },
      {
        question: "Potential savings in time, money, or resources",
        options: ["<5%", "5-20%", "21-50%", ">50%"],
      },
      {
        question: "Priority level of the problem (Frequency/Severity)",
        options: ["Rarely", "Sometimes", "Often", "Very Often"],
      },
    ],
  },
  {
    category: "2. Market Potential",
    items: [
      {
        question: "Total Addressable Market (TAM) size",
        options: ["<$100M", "$100M-$500M", "$500M-$1B", ">$1B"],
      },
      {
        question: "Growth rate of the market",
        options: ["<5%", "5-10%", "10-20%", ">20%"],
      },
    ],
  },
];

const DueDiligenceForm = () => {
  const [formData, setFormData] = useState<{ [key: string]: string }>({});

  const handleChange = (question: string, value: string) => {
    setFormData((prev) => ({ ...prev, [question]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Submitted Data:", formData);
  };

  return (
    <div className="max-w-2xl mx-auto mt-6 bg-white dark:bg-gray-800 p-6 shadow-lg rounded-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">Due Diligence Checklist</h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        {questions.map((section, index) => (
          <div key={index}>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">{section.category}</h3>
            {section.items.map((item, idx) => (
              <div key={idx} className="mb-4">
                <label className="block text-gray-900 dark:text-white">{item.question}</label>
                <select
                  className="w-full p-2 border rounded mt-1 bg-white text-gray-900 dark:bg-gray-700 dark:text-white"
                  value={formData[item.question] || ""}
                  onChange={(e) => handleChange(item.question, e.target.value)}
                >
                  <option value="" disabled>Select an option</option>
                  {item.options.map((option, optIdx) => (
                    <option key={optIdx} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        ))}
        <button type="submit" className="w-full bg-green-500 text-white p-2 rounded">
          Submit
        </button>
      </form>
    </div>
  );
};

export default DueDiligenceForm;
