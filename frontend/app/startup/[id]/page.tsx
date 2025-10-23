"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Startup } from "@/types/startup";
import { StartupScoreDetails } from "@/types/startup";

export default function StartupDetailsPage() {
  const { id } = useParams();
  const router = useRouter();
  const [startup, setStartup] = useState<Startup | null>(null);
  const [scoreDetails, setScoreDetails] = useState<StartupScoreDetails | null>(null);

  useEffect(() => {
    const fetchStartup = async () => {
      try {
        const res = await fetch(`/api/startups/${id}`);
        if (!res.ok) throw new Error("Не удалось загрузить стартап");
        const data = await res.json();
        setStartup(data);
      } catch (err) {
        console.error("Ошибка при получении стартапа:", err);
      }
    };

    const fetchScoreDetails = async () => {
      try {
        const res = await fetch(`/api/startups/batch/pitch-scores?ids=${id}`);
        if (!res.ok) throw new Error("Не удалось загрузить скоринг");
        const data = await res.json();
        const score = data[id as string];
        setScoreDetails(score || null);
      } catch (err) {
        console.error("Ошибка при получении скоринга:", err);
      }
    };

    if (id) {
      fetchStartup();
      fetchScoreDetails();
    }
  }, [id]);

  if (!startup) return <p className="text-gray-500">Загрузка...</p>;

  return (
    <div className="max-w-3xl mx-auto p-6 bg-gray-300 rounded shadow space-y-4 text-black">
      <h3 className="text-lg font-bold text-black mb-2">{startup.name}</h3>
      <p>
        <strong>Industry:</strong>{" "}
        {Array.isArray(startup.industry)
          ? startup.industry.join(", ")
          : startup.industry}
      </p>
      <p>
        <strong>Stage:</strong>{" "}
        {Array.isArray(startup.stage)
          ? startup.stage.join(", ")
          : startup.stage}
      </p>
      <p>
        <strong>Region:</strong>{" "}
        {Array.isArray(startup.region)
          ? startup.region.join(", ")
          : startup.region}
      </p>

      <p><strong>Check Size:</strong> ${startup.min_check.toLocaleString()}</p>
      <p className="mt-2 text-sm text-gray-700">{startup.description}</p>

      {scoreDetails && (
        <div className="mt-4 bg-white p-4 rounded shadow">
          <h4 className="font-semibold mb-2 text-black">📊 Pitch Deck Score</h4>
          <table className="w-full text-sm text-left text-black">
            <tbody>
            <tr><td className="py-1 pr-4 font-medium">USP</td><td>{typeof scoreDetails.usp === "number" ? scoreDetails.usp : "—"}</td></tr>
            <tr><td className="py-1 pr-4 font-medium">Market</td><td>{typeof scoreDetails.market === "number" ? scoreDetails.market : "—"}</td></tr>
            <tr><td className="py-1 pr-4 font-medium">Business Model</td><td>{typeof scoreDetails.business_model === "number" ? scoreDetails.business_model : "—"}</td></tr>
            <tr><td className="py-1 pr-4 font-medium">Team</td><td>{typeof scoreDetails.team === "number" ? scoreDetails.team : "—"}</td></tr>
            <tr><td className="py-1 pr-4 font-medium">Finance</td><td>{typeof scoreDetails.finance === "number" ? scoreDetails.finance : "—"}</td></tr>
            </tbody>
          </table>
        </div>
      )}

      <button
        onClick={() => router.push("/sourcing")}
        className="mt-6 inline-block px-4 py-2 bg-blue-400 text-black rounded hover:bg-gray-300 transition"
      >
        ← Назад
      </button>
    </div>
  );
}
