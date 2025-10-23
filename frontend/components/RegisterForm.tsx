"use client";
import { useState } from "react";
import { registerUser } from "@/utils/auth";
import { useRouter } from "next/navigation";

export default function RegisterForm() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    role: "investor",
    company_name: "",
    contacts: "",
    full_name: "",
  });
  const [error, setError] = useState("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const validateForm = () => {
    for (const key in formData) {
      if ((formData as any)[key].trim() === "") {
        setError("Пожалуйста, заполните все поля.");
        return false;
      }
    }
    return true;
  };

  const handleRegister = async () => {
    setError("");

    if (!validateForm()) return;

    try {
      await registerUser(formData);
      
      // ✅ Сохраняем роль сразу после успешной регистрации
      localStorage.setItem("user_role", formData.role);
      
      router.push("/auth"); // Перенаправляем на страницу входа
    } catch (err: any) {
      setError(err.message || "Ошибка регистрации");
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 p-6 border rounded bg-gray-200 shadow">
      <h2 className="text-black text-xl font-bold mb-4">Registration</h2>

      {error && <div className="text-red-500 mb-2">{error}</div>}

      {[
        ["email", "Email"],
        ["full_name", "Name     Last Name"],
        ["company_name", "Company"],
        ["contacts", "Contacts"],
        ["password", "Password"],
      ].map(([key, label]) => (
        <div className="mb-3" key={key}>
          <label className="block text-black text-sm font-bold">{label}</label>
          <input
            name={key}
            type={
              key === "email" ? "email" :
              key === "password" ? "password" : "text"
            }
            minLength={key === "password" ? 8 : undefined}
            required
            value={(formData as any)[key]}
            onChange={handleChange}
            className="w-full border p-2 rounded text-black"
          />
        </div>
      ))}

      <div className="mb-4">
        <label className="block text-black text-sm font-medium">Role</label>
        <select
          name="role"
          value={formData.role}
          onChange={handleChange}
          className="w-full border p-2 rounded  text-black"
        >
          <option value="investor">Investor</option>
          <option value="founder">Founder</option>
        </select>
      </div>

      <button
        onClick={handleRegister}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded shadow"
      >
        REGISTRATION
      </button>
    </div>
  );
}
