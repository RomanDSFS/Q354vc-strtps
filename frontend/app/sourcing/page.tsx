// ✅ page.tsx
"use client";

import React, { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation"; // 👈 добавляем
import Pipeline from "@/components/sourcing/Pipeline";
import SearchFilters from "@/components/sourcing/SearchFilters";
import FilterBar from "@/components/sourcing/FilterBar";
import StartupList from "@/components/sourcing/StartupList";
import { fetchMatchedStartups, sendToDueDiligence, getInvestorProfile } from "@/utils/api";
import { fetchUserProfile } from "@/utils/auth";
import { Startup } from "@/types/startup";

export default function SourcingPage() {
  const [currentStage, setCurrentStage] = useState("Sourcing");
  const [allStartups, setAllStartups] = useState<Startup[]>([]);
  const [filteredStartups, setFilteredStartups] = useState<Startup[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [profileLoaded, setProfileLoaded] = useState(false);

  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    const loadInvestorProfileAndStartups = async () => {
      try {
        const { user_id } = await fetchUserProfile();
        if (!user_id) {
          console.warn("⚠️ Не удалось получить user_id");
          return;
        }

        const profile = await getInvestorProfile(user_id);
        console.log("👤 Profile loaded:", profile);

        if (!profile) return;

        setProfileLoaded(true);

        const startups = await fetchMatchedStartups(user_id);
        console.log("📦 Стартапов получено:", startups.length);

        setAllStartups(startups);
        setFilteredStartups(startups);
      } catch (err) {
        console.warn("⚠️ Не удалось загрузить профиль или стартапы", err);
      }
    };

    const isEditMode = searchParams.get("edit") === "true";
    setIsEditing(isEditMode);

    if (!isEditMode) {
      loadInvestorProfileAndStartups();
    }
  }, [searchParams]);

  const handleSearchApply = async (startups: Startup[]) => {
    setAllStartups(startups);
    setFilteredStartups(startups);
    setProfileLoaded(true);
    setIsEditing(false);

    // После применения фильтров убираем ?edit из URL
    router.push("/sourcing");
  };

  const handleListFilterChange = (filters: any) => {
    const filtered = allStartups.filter((s) => {
      const check = parseFloat(filters.checkSize?.replace(/[^\d]/g, "")) || 0;
      return (
        (!filters.stage || s.stage.includes(filters.stage)) &&
        (!filters.industry || s.industry.includes(filters.industry)) &&
        (!filters.region || s.region.includes(filters.region)) &&
        (!filters.checkSize || s.min_check <= check)
      );
    });
    setFilteredStartups(filtered);
  };

  const handleSendToDD = async (startupId: string) => {
    try {
      await sendToDueDiligence(startupId);
      console.log("Стартап отправлен в Due Diligence");
    } catch (err) {
      console.error("Ошибка при отправке:", err);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <Pipeline currentStage={currentStage} onStageClick={setCurrentStage} />

      {(!profileLoaded || isEditing) && (
        <SearchFilters onApplyFilters={handleSearchApply}
        onHideFilters={() => setIsEditing(false)}
        />
      )}

      {profileLoaded && !isEditing && (
        <>
          <FilterBar onFilterChange={handleListFilterChange} />
          <StartupList startups={filteredStartups} onSendToDD={handleSendToDD} />
        </>
      )}

      {filteredStartups.length === 0 && profileLoaded && !isEditing && (
        <p className="text-gray-500 text-center mt-4">Нет подходящих стартапов по текущим критериям.</p>
      )}
    </div>
  );
}
