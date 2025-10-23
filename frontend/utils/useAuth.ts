import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

// ⛔️ Только редирект, если нет авторизации
export function useAuthGuard(requiredRole?: string) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push("/auth");
      } else if (requiredRole && user.role !== requiredRole) {
        router.push("/unauthorized"); // или /dashboard
      }
    }
  }, [user, isLoading, router, requiredRole]);
}
