"use client";
import React, { useState, useEffect } from "react";

interface FilterBarProps {
  onFilterChange: (filters: {
    stage: string;
    industry: string;
    region: string;
    checkSize: string;
  }) => void;
}

const stages = ["Pre-Seed", "Seed", "Series A", "Growth"];
const industries = ["SaaS", "AI", "Tech", "FinTech", "Healthcare"];
const regions = ["USA", "EU", "Asia", "LATAM"];
const checkSizes = ["30 000", "50 000", "100 000", "200 000", "500 000", "700 000"];

export default function FilterBar({ onFilterChange }: FilterBarProps) {
  const [stage, setStage] = useState("");
  const [industry, setIndustry] = useState("");
  const [region, setRegion] = useState("");
  const [checkSize, setCheckSize] = useState("");

  // Вызываем родительский onFilterChange при изменении фильтров
  useEffect(() => {
    onFilterChange({ stage, industry, region, checkSize });
  }, [stage, industry, region, checkSize]);

  const handleReset = () => {
    setStage("");
    setIndustry("");
    setRegion("");
    setCheckSize("");
  };

  const hasActiveFilters = stage || industry || region || checkSize;

  return (
    <div
      className={`flex flex-wrap items-end gap-6 p-4 border rounded-lg 
      ${hasActiveFilters ? "bg-blue-50 border-blue-400" : "bg-gray-400 border-gray-300"} 
      text-black font-medium relative`}
    >
      {hasActiveFilters && (
        <div className="absolute -top-3 left-4 text-xs text-blue-600 font-semibold bg-white px-2">
          Фильтры применены
        </div>
      )}

      {/* Стадия */}
      <div className="flex flex-col">
        <label className="text-sm font-bold mb-1">Stage</label>
        <select
          value={stage}
          onChange={(e) => setStage(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">—</option>
          {stages.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {/* Индустрия */}
      <div className="flex flex-col">
        <label className="text-sm font-bold mb-1">Industry</label>
        <select
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">—</option>
          {industries.map((i) => (
            <option key={i} value={i}>
              {i}
            </option>
          ))}
        </select>
      </div>

      {/* Регион */}
      <div className="flex flex-col">
        <label className="text-sm font-bold mb-1">Region</label>
        <select
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">—</option>
          {regions.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      {/* Чек */}
      <div className="flex flex-col">
        <label className="text-sm font-bold mb-1">Check</label>
        <select
          value={checkSize}
          onChange={(e) => setCheckSize(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="">—</option>
          {checkSizes.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      {/* Кнопка сброса */}
      {hasActiveFilters && (
        <button
          onClick={handleReset}
          className="ml-auto px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 text-sm"
        >
          Сбросить фильтры
        </button>
      )}
    </div>
  );
}
