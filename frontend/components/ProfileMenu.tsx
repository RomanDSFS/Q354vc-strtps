"use client";
import { logoutUser } from "@/utils/auth";

export default function ProfileMenu() {
  return (
    <div className="absolute right-0 mt-2 w-48 bg-white border rounded shadow-lg z-50">
      <ul className="py-1 text-sm text-gray-700">
        <li>
          <a href="/settings" className="block px-4 py-2 hover:bg-gray-100">
            Настройки
          </a>
        </li>
        <li>
          <button
            onClick={logoutUser}
            className="w-full text-left px-4 py-2 hover:bg-red-100 text-red-600"
          >
            Выйти
          </button>
        </li>
      </ul>
    </div>
  );
}
