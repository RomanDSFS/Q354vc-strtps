import { Startup } from "@/types/startup";

// Универсальный fetch с заголовками и обработкой ошибок
async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("token");

  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API error: ${res.status} - ${errorText}`);
  }

  return res.json();
}

// ✅ Утилита: нормализация чека (поддержка string | string[])
const normalizeCheck = (check: string | string[] | undefined): number => {
  if (!check) return 0;
  const raw = Array.isArray(check) ? check[0] : check;
  return parseFloat(raw.replace(/[^\d.]/g, "")) || 0;
};

// ✅ Сохранение профиля инвестора
export async function saveInvestorProfile(filters: {
  investor_type: string;               // по-прежнему один
  investment_stage: string[];
  industry: string[];
  region: string[];
  checkSize: string | string[] | undefined; // теперь безопасно
}) {
  const payload = {
    investor_type: filters.investor_type ? [filters.investor_type] : [],
    investment_stage: filters.investment_stage,
    industry: filters.industry,
    region: filters.region,
    min_check: normalizeCheck(filters.checkSize), // ✅ безопасная очистка
  };
  console.log("📤 Payload:", payload); // лог для отладки
  
  return apiFetch("/api/startups/investors/profile", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// ✅ Получение подходящих стартапов по investor_id
export async function fetchMatchedStartups(investorId: string) {
  return apiFetch<{ startups: Startup[] }>(`/api/startups/matches/me`).then(
    (res) => res.startups
  );
}

// 🔹 Отправка стартапа в Due Diligence
export async function sendToDueDiligence(startupId: string) {
  return apiFetch<{ message: string }>(`/api/startups/select/${startupId}`, {
    method: "POST",
  });
}
// ✅ Получение сохранённого профиля инвестора
export async function getInvestorProfile(investorId: string) {
  return apiFetch<{
    investor_type: string;
    investment_stage: string[];
    industry: string[];
    region: string[];
    min_check: number;
  }>(`/api/investors/profile/${investorId}`);
}
export { apiFetch };

