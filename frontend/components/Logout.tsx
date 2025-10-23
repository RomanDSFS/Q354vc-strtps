"use client";
import { useRouter } from "next/navigation";
import { clearAuth } from "@/utils/auth";

export default function Logout() {
    const router = useRouter();

    const handleLogout = async () => {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
            clearAuth();
            router.push("/auth");
            return;
        }

        await fetch("http://127.0.0.1:8001/auth/logout", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });

        clearAuth();
        router.push("/auth");
    };

    return (
        <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded">
            Выйти
        </button>
    );
}
