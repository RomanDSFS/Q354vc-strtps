// ✅ Navbar.tsx
"use client";
import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { logoutUser } from "@/utils/auth";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Navbar() {
  const { user, isLoading } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const router = useRouter();

  const toggleDropdown = () => setDropdownOpen(!dropdownOpen);

  const handleEditProfile = () => {
    router.push("/sourcing?edit=true"); // ✅ теперь через query
  };

  return (
    <nav className="flex justify-end items-center p-8 bg-gray-600 h-10 relative z-40">
      {!isLoading && user ? (
        <div className="relative">
          <button
            onClick={toggleDropdown}
            className="text-white font-semibold focus:outline-none"
          >
            👤 {user.email}
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50">
              <ul className="py-1 text-sm text-gray-700">
                <li>
                  <button
                    onClick={handleEditProfile}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    🛠 Редактировать профиль
                  </button>
                </li>
                <li>
                  <Link href="/settings" className="block px-4 py-2 hover:bg-gray-100">
                    ⚙️ Настройки
                  </Link>
                </li>
                <li>
                  <button
                    onClick={logoutUser}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    🚪 Выйти
                  </button>
                </li>
              </ul>
            </div>
          )}
        </div>
      ) : (
        <Link href="/auth">
          <button className="bg-blue-500 hover:bg-blue-700 text-white px-4 py-2 rounded">
            Sign In
          </button>
        </Link>
      )}
    </nav>
  );
}
