"use client";
import React, { useState } from "react";
import { saveInvestorProfile, fetchMatchedStartups} from "@/utils/api";
import { useRouter } from "next/navigation";

interface SearchFiltersProps {
  onApplyFilters: (startups: any[]) => void;
  onHideFilters: () => void; // ✅ Новый пропс для скрытия фильтров
}

const investorTypes = ["VC", "PE", "CVC", "Angels"];
const stages = ["Pre-Seed", "Seed", "Series A", "Growth"];
const industries = ["SaaS", "AI", "Tech", "FinTech", "Healthcare"];
const regions = ["USA", "EU", "Asia", "LATAM"];
const checkSizes = ["30 000", "50 000", "100 000", "200 000", "500 000", "700 000"];

export default function SearchFilters({ onApplyFilters, onHideFilters }: SearchFiltersProps) {
  const [investorType, setInvestorType] = useState("");
  const [selectedStages, setSelectedStages] = useState<string[]>([]);
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [checkSize, setCheckSize] = useState("");
  //const [isSubmitted, setIsSubmitted] = useState(false);

  //const router = useRouter();

  const toggle = (value: string, list: string[], setList: (v: string[]) => void) => {
    if (list.includes(value)) {
      setList(list.filter((item) => item !== value));
    } else {
      setList([...list, value]);
    }
  };

  const handleSubmit = async () => {
    try {
      if (!investorType || selectedStages.length === 0 || selectedIndustries.length === 0 || selectedRegions.length === 0) {
        alert("Выберите все обязательные фильтры");
        return;
      }

      await saveInvestorProfile({
        investor_type: investorType,
        investment_stage: selectedStages,
        industry: selectedIndustries,
        region: selectedRegions,
        checkSize,
      });

      const investorId = localStorage.getItem("user_id");
      if (!investorId) throw new Error("Investor ID не найден в localStorage");

      const startups = await fetchMatchedStartups(investorId);
      onApplyFilters(startups);

      //setIsSubmitted(true);
    } catch (err) {
      console.error("❌ Ошибка получения стартапов:", err);
      alert("Ошибка при загрузке подходящих стартапов.");
    }
  };

  const resetFilters = () => {
    setInvestorType("");
    setSelectedStages([]);
    setSelectedIndustries([]);
    setSelectedRegions([]);
    setCheckSize("");
  };
   /*
  const handleHideFilters = async () => {
    try {
      const investorId = localStorage.getItem("user_id");
      if (!investorId) throw new Error("User ID не найден в localStorage");

      const profile = await getInvestorProfile(investorId);
      if (profile) {
        router.push("/sourcing");
      } else {
        alert("Профиль инвестора ещё не заполнен. Пожалуйста, заполните его перед выходом.");
      }
    } catch (error) {
      console.error("Ошибка при проверке профиля:", error);
      alert("Не удалось проверить профиль. Пожалуйста, попробуйте снова.");
    }
  };

  if (isSubmitted) return null;*/

  return (
    <div className="flex flex-wrap items-end gap-4 bg-gray-300 px-8 py-4 shadow rounded-lg text-black font-medium">
      
      {/* Тип инвестора */}
      <div className="flex flex-col ">
        <label className="text-sm font-bold mb-1 py-2">Investor type</label>
        <select
          value={investorType}
          onChange={(e) => setInvestorType(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">—</option>
          {investorTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      {/* Стадии */}
      <div className="flex flex-col">
        <label className="text-sm font-bold mb-1">Stages</label>
        <div className="flex flex-wrap gap-1 max-w-xs">
          {stages.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => toggle(s, selectedStages, setSelectedStages)}
              className={`px-3 py-1 border rounded ${
                selectedStages.includes(s) ? "bg-blue-600 text-white" : "bg-gray-200"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Индустрии */}
      <div className="flex flex-col">
        <label className="text-sm font-bold mb-1">Industries</label>
        <div className="flex flex-wrap gap-1 max-w-xs">
          {industries.map((i) => (
            <button
              key={i}
              type="button"
              onClick={() => toggle(i, selectedIndustries, setSelectedIndustries)}
              className={`px-3 py-1 border rounded ${
                selectedIndustries.includes(i) ? "bg-blue-600 text-white" : "bg-gray-200"
              }`}
            >
              {i}
            </button>
          ))}
        </div>
      </div>

      {/* Регионы */}
      <div className="flex flex-col">
        <label className="text-sm font-bold mb-1">Regions</label>
        <div className="flex flex-wrap gap-1 max-w-xs">
          {regions.map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => toggle(r, selectedRegions, setSelectedRegions)}
              className={`px-3 py-1 border rounded ${
                selectedRegions.includes(r) ? "bg-blue-600 text-white" : "bg-gray-200"
              }`}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      {/* Чек */}
      <div className="flex flex-col">
        <label className="text-sm font-bold mb-1">Check size</label>
        <select
          value={checkSize}
          onChange={(e) => setCheckSize(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">—</option>
          {checkSizes.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Кнопки */}
      <div className="flex flex-row gap-2 mt-4">
        <button
          onClick={handleSubmit}
          className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
        >
          APPLY
        </button>
        <button
          onClick={resetFilters}
          className="bg-gray-400 text-black px-6 py-2 rounded hover:bg-gray-500"
        >
          RESET
        </button>
        <button
          onClick={onHideFilters}
          className="bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600"
        >
          HIDE
        </button>
      </div>
    </div>
  );
}
