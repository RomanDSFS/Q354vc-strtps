"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Startup } from "@/types/startup";

interface StartupListProps {
  startups: Startup[];
  onSendToDD: (startupId: string) => void;
}

export default function StartupList({ startups, onSendToDD }: StartupListProps) {
  const router = useRouter();
  const [scores, setScores] = useState<Record<string, number>>({});

  useEffect(() => {
    const fetchScores = async () => {
      const ids = startups.map((s) => s.id).join(",");
      try {
        const res = await fetch(`/api/startups/batch/pitch-scores?ids=${ids}`);
        if (!res.ok) throw new Error("Ошибка загрузки скоринга");
  
        const data: Record<string, any> = await res.json();
  
        const processed: Record<string, number> = {};
        for (const [id, raw] of Object.entries(data)) {
          const scoreObj = raw as { total?: number } | null;
  
          if (scoreObj && typeof scoreObj.total === "number") {
            processed[id] = Math.round(scoreObj.total); // или использовать .toFixed(1)
          } else {
            processed[id] = 0; // Fallback на случай отсутствия данных
          }
        }
  
        setScores(processed);
      } catch (err) {
        console.error("⚠️ Ошибка получения скорингов:", err);
      }
    };
  
    if (startups.length > 0) {
      fetchScores();
    }
  }, [startups]);

  if (startups.length === 0) {
    return <p className="text-gray-500 mt-4">Стартапы не найдены.</p>;
  }

  return (
    <div className="overflow-x-auto mt-6">
      <table className="min-w-full table-auto border-collapse bg-gray-400 rounded shadow text-sm text-left">
        <thead>
          <tr className="bg-gray-100 text-black font-semibold">
            <th className="px-4 py-2">More</th>
            <th className="px-4 py-2">Name</th>
            <th className="px-4 py-2">Stage</th>
            <th className="px-4 py-2">Industry</th>
            <th className="px-4 py-2">Region</th>
            <th className="px-4 py-2">Check Size</th>
            <th className="px-4 py-2">Score</th>
            <th className="px-4 py-2 text-right">To D_D</th>
          </tr>
        </thead>
        <tbody>
          {startups.map((startup) => (
            <tr key={startup.id} className="border-b hover:bg-gray-50">
              <td className="px-4 py-2">
                <button
                  className="text-blue-600 hover:underline font-medium"
                  onClick={() => router.push(`/startup/${startup.id}`)}
                >
                  More
                </button>
              </td>
              <td className="px-4 py-2 font-semibold text-black">{startup.name}</td>
              <td className="px-4 py-2 text-black">{startup.stage.join(", ")}</td>
              <td className="px-4 py-2 text-black">{startup.industry.join(", ")}</td>
              <td className="px-4 py-2 text-black">{startup.region.join(", ")}</td>
              <td className="px-4 py-2 text-black">${startup.min_check.toLocaleString()}</td>
              <td className="px-4 py-2 text-black">{scores[startup.id] ?? 0}
              </td>
              <td className="px-4 py-2 text-right">
                <button
                  onClick={() => onSendToDD(startup.id)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded text-sm"
                >
                  To D_D
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}