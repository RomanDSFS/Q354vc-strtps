"use client";
import React, { useState, useEffect } from "react";
import { apiFetch } from "@/utils/api";
import { FounderProfile } from "@/types/founder";


const FounderProfileForm = () => {
  const [form, setForm] = useState<FounderProfile>({
    name: "",
    description: "",
    stage: "",
    industry: "",
    region: "",
    min_check: 0,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // ✅ Проверка профиля при монтировании
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const profile: FounderProfile = await apiFetch("/api/startups/founders/profile");
        if (profile && profile.name) {
          setForm(profile);
          setIsSubmitted(true);
        }
      } catch (err) {
        console.warn("Профиль фаундера не найден. Отображаем форму.");
      }
    };

    fetchProfile();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "min_check" ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await apiFetch("/api/startups/founders/profile", {
        method: "POST",
        body: JSON.stringify({
          name: form.name,
          description: form.description,
          stage: [form.stage],
          industry: [form.industry],
          region: [form.region],
          min_check: form.min_check,
        }),
      });

      setIsSubmitted(true);
      setShowSuccess(true);

      setTimeout(() => {
        setShowSuccess(false);
      }, 3000);
    } catch (err) {
      console.error("Ошибка при сохранении профиля", err);
      alert("Ошибка при сохранении профиля");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = () => {
    setIsSubmitted(false);
  };
  const handleHide = () => setIsSubmitted(true); // просто скрываем форму

  return (
    <div className="relative bg-gray-300 p-6 rounded shadow text-black">
      {!isSubmitted ? (
        <>
          {/* Кнопка Hide */}
          <button
            onClick={handleHide}
            className="absolute top-6 right-8 inline-flex items-center gap-2 
            px-3 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-sm hover:bg-blue-700 transition-colors duration-200"
          >
            <span className="text-white text-lg leading-none">▲</span>
            Hide
          </button>

          <h2 className="text-lg font-bold mb-4">Basic information about the startup</h2>

          <div className="space-y-4">
            <div>
              <label className="block font-bold mb-1 text-black">Startup Name</label>
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                className="w-full p-2 border rounded"
              />
            </div>

            <div>
              <label className="block font-bold mb-1 text-black">Brief description (10-20 words)</label>
              <input
                type="text"
                name="description"
                value={form.description}
                onChange={handleChange}
                className="w-full p-2 border rounded"
              />
            </div>

            <div>
              <label className="block font-bold mb-1 text-black">Stage investment</label>
              <select name="stage" value={form.stage} onChange={handleChange}
                className="w-full p-2 border rounded text-black">
                <option value="">Select...</option>
                <option value="Pre-Seed">Pre-Seed</option>
                <option value="Seed">Seed</option>
                <option value="Series A">Series A</option>
                <option value="Series B">Series B</option>
              </select>
            </div>

            <div>
              <label className="block font-bold mb-1 text-black">Industry</label>
              <select name="industry" value={form.industry} onChange={handleChange}
                className="w-full p-2 border rounded text-black">
                <option value="">Select...</option>
                <option value="AI">AI</option>
                <option value="Fintech">Fintech</option>
                <option value="HealthTech">HealthTech</option>
              </select>
            </div>

            <div>
              <label className="block font-bold mb-1 text-black">Region</label>
              <select name="region" value={form.region} onChange={handleChange}
                className="w-full p-2 border rounded text-black">
                <option value="">Select...</option>
                <option value="EU">EU</option>
                <option value="US">US</option>
                <option value="Asia">Asia</option>
              </select>
            </div>

            <div>
              <label className="block font-bold mb-1 text-black">Minimum check ($)</label>
              <input
                type="number"
                name="min_check"
                value={form.min_check}
                onChange={handleChange}
                className="w-full p-2 border rounded"
              />
            </div>

            <div>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                {isSubmitting ? "Сохраняем..." : "APPLY"}
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="space-y-4">
          {showSuccess && (
            <p className="text-green-700 font-bold mb-1 ">
              ✅ Profile successfully updated.
            </p>
          )}

          {!showSuccess && (
            <button
              onClick={handleEdit}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-sm hover:bg-blue-700 transition-colors duration-200"
            >
              <span className="text-white text-lg leading-none">▼</span>
              Edit Profile
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default FounderProfileForm;
