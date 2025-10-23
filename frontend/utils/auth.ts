// ✅ Получение профиля пользователя
export async function fetchUserProfile() {
  const token = localStorage.getItem("token");
  if (!token) return null;

  try {
    const response = await fetch("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) throw new Error("Не удалось получить данные пользователя");

    const profile = await response.json();
    setUserRole(profile.role);
    localStorage.setItem("user_id", profile.id);
    
    return profile;
  } catch (err) {
    console.error("❌ Ошибка получения профиля:", err);
    return null;
  }
}

// ✅ Установка и получение роли
export const setUserRole = (role: string) => {
  localStorage.setItem("user_role", role);
};

export const getUserRole = (): string | null => {
  return localStorage.getItem("user_role");
};

// ✅ Очистка всех auth-данных
export const clearAuth = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user_role");
  localStorage.removeItem("user_id");
};

// ✅ Вход пользователя через API Gateway (правильный Content-Type!)
export const loginUser = async (email: string, password: string) => {
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded", // 🔥 Ключевой момент
      },
      body: new URLSearchParams({
        grant_type: "password", // ✅ ОБЯЗАТЕЛЬНО!
        username: email, // ⬅️ OAuth2 требует "username", не "email"
        password: password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      const detail =
        typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail || "Ошибка авторизации");

      throw new Error(detail);
    }

    // ✅ Сохраняем токены и данные
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    //localStorage.setItem("user_id", data.user.id);
    //localStorage.setItem("user_role", data.user.role);

    return data;
  } catch (error: any) {
    console.error("❌ Ошибка входа:", error.message);
    throw error;
  }
};

// ✅ Регистрация пользователя
export const registerUser = async (formData: {
  email: string;
  password: string;
  role: string;
  company_name: string;
  contacts: string;
  full_name: string;
}) => {
  try {
    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Ошибка регистрации");
    }

    return await response.json();
  } catch (error: any) {
    console.error("Ошибка регистрации:", error.message);
    throw error;
  }
};

// ✅ Выход
export const logoutUser = async () => {
  const refreshToken = localStorage.getItem("refresh_token");

  if (refreshToken) {
    await fetch("/api/auth/logout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  clearAuth();
  window.location.href = "/auth";
};
