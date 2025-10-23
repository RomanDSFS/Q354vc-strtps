"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { loginUser, fetchUserProfile, setUserRole } from "@/utils/auth";
import { useAuth } from "@/context/AuthContext"; // ✅ контекст

export default function AuthForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const { setUser } = useAuth(); // ✅ получаем setUser из контекста

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      await loginUser(email, password); // ⬅️ токены уже сохраняются внутри

      const profile = await fetchUserProfile();
      if (!profile) throw new Error("Не удалось получить профиль");

      setUser(profile); // ✅ обновляем контекст
      setUserRole(profile.role); // ⬅️ оставим для совместимости

      // 🔁 Редирект по роли
      if (profile.role === "investor") {
        router.push("/sourcing");
      } else if (profile.role === "founder") {
        router.push("/startups");
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      console.error("Ошибка входа:", err);
      setError(err.message || "Ошибка авторизации. Проверьте email и пароль.");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-2xl font-bold mb-4">Sign In</h2>
      {error && <p className="text-red-500 mb-2">{error}</p>}

      <form onSubmit={handleLogin} className="space-y-4">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="border p-2 w-64 text-black"
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="border p-2 w-64 text-black"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded font-bold w-full"
        >
          Войти
        </button>
      </form>

      <p className="text-sm text-center mt-4">
        Нет аккаунта?{" "}
        <a
          href="/auth/register"
          className="text-blue-600 hover:underline font-bold"
        >
          Регистрация
        </a>
      </p>
    </div>
  );
}
