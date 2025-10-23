"use client";
import { createContext, useContext, useEffect, useState } from "react";
import { fetchUserProfile } from "@/utils/auth";

// Тип данных пользователя
interface User {
  id: string;
  email: string;
  role: string;
  [key: string]: any; // можно расширять под нужды
}

// Тип контекста
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  setUser: (user: User | null) => void; // ✅ добавили
}

// 👉 Создаём контекст
const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  setUser: () => {},
});

// ✅ Провайдер оборачивает всё приложение
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // ⏳ Загружаем профиль при старте
  useEffect(() => {
    const initUser = async () => {
      const profile = await fetchUserProfile();
      setUser(profile);
      setIsLoading(false);
    };
    initUser();
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading,setUser  }}>
      {children}
    </AuthContext.Provider>
  );
};

// ✅ Хук доступа к контексту из любого компонента
export const useAuth = () => useContext(AuthContext);
