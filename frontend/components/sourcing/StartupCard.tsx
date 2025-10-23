"use client";
import React from "react";
import { Startup } from "@/types/startup";

interface StartupCardProps {
  startup: Startup;
  onSendToDD: (startupId: string) => void;
}

export default function StartupCard({
  startup,
  onSendToDD,
}: StartupCardProps) {
  return (
    <div className="bg-gray-900 border rounded-xl p-4 shadow hover:shadow-md transition-all 
                    flex flex-col justify-between h-full text-black">
      {/* 🔹 Название стартапа */}
      <h3 className="text-lg font-bold text-black mb-2">{startup.name}</h3>

      {/* 🔹 Индустрия */}
      <p className="text-sm text-black mb-1 line-clamp-2">
        <span className="font-semibold">Industry:</span>{" "}
        {startup.industry.join(", ")}
      </p>

      {/* 🔹 Стадия */}
      <p className="text-sm text-black mb-1 line-clamp-2">
        <span className="font-semibold">Stage:</span>{" "}
        {startup.stage.join(", ")}
      </p>

      {/* 🔹 Регион */}
      <p className="text-sm text-black mb-2 line-clamp-2">
        <span className="font-semibold">Region:</span>{" "}
        {startup.region.join(", ")}
      </p>

      {/* 🔹 Кнопка To D_D */}
      <button
        onClick={() => onSendToDD(startup.id)}
        className="mt-auto w-fit px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition"
      >
        To D_D
      </button>
    </div>
  );
}
