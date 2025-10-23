"use client";
import React from "react";
import { useRouter } from "next/navigation";

const stages = [
  "Sourcing",
  "Due Diligence",
  "Deal Room",
  "Collaboration",
  "Monitoring",
  "Exit",
];

interface PipelineProps {
  currentStage?: string;
  onStageClick?: (stage: string) => void;
}

export default function Pipeline({
  currentStage = "Sourcing",
  onStageClick,
}: PipelineProps) {
  const router = useRouter();
  const currentIndex = stages.findIndex((s) => s === currentStage);

  const handleStageClick = (stage: string) => {
    if (stage === "Sourcing") {
      router.push("/sourcing"); // 🔥 Редирект на /sourcing при клике на "Sourcing"
    } else {
      onStageClick?.(stage); // 🔁 Передаём наружу для остальных этапов
    }
  };

  return (
    <div className="flex w-full overflow-x-auto select-none mt-[-10px]">
      {stages.map((stage, index) => {
        const isActive = index === currentIndex;
        const isCompleted = index < currentIndex;

        return (
          <div
            key={stage}
            onClick={() => handleStageClick(stage)} // 👈 Используем новую обработку
            className={`relative flex-1 text-center text-sm font-semibold py-3 px-2 cursor-pointer transition-all
              ${isActive ? "bg-blue-600 text-white" : isCompleted ? "bg-blue-400 text-white" : "bg-gray-300 text-gray-700"}
              hover:brightness-110
            `}
            style={{
              clipPath:
                index === stages.length - 1
                  ? "polygon(0 0, 100% 0, 100% 100%, 0% 100%)"
                  : "polygon(0 0, 95% 0, 100% 50%, 95% 100%, 0% 100%)",
            }}
            title={stage}
          >
            {stage}
          </div>
        );
      })}
    </div>
  );
}
