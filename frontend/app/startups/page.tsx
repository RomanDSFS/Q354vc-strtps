"use client";
import React, { useState } from "react";
import UploadPitchDeck from "@/components/UploadPitchDeck";
import DueDiligenceForm from "@/components/DueDiligenceForm";
import FounderProfileForm from "@/components/founder/FounderProfileForm";

const StartupsPage = () => {
  const [showChecklist, setShowChecklist] = useState(false);

  return (
    <div className="p-10 ml-64">
      <h1 className="text-3xl font-bold">For Founders</h1>
      <p className="mt-4 font-bold">Select one of the options:</p>

      {/* ✅ Форма профиля фаундера */}
      <FounderProfileForm />

      <div className="mt-6 flex space-x-4">
        <button
          className="bg-blue-600 font-bold text-white px-4 py-2 rounded"
          onClick={() => setShowChecklist(false)}
        >
          Upload Pitch Deck
        </button>

        <button
          className="bg-green-500 text-white px-4 py-2 rounded"
          onClick={() => setShowChecklist(true)}
        >
          Fill Due Diligence Checklist
        </button>
      </div>

      <div className="mt-6">
        {!showChecklist ? <UploadPitchDeck /> : <DueDiligenceForm />}
      </div>
    </div>
  );
};

export default StartupsPage;
