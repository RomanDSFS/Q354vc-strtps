"use client";
import React, { useState } from "react";

const UploadPitchDeck = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setMessage(""); // сброс предыдущих сообщений
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setMessage("❌ Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const token = localStorage.getItem("token");

    try {
      setIsUploading(true);
      const res = await fetch("/api/startups/founders/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token || ""}`,
        },
        body: formData,
      });

      if (!res.ok) throw new Error("Ошибка загрузки");

      const result = await res.json();
      setMessage("✅ Pitch Deck uploaded and processed successfully.");
      console.log("Результат:", result);
      setFile(null); // сброс формы
    } catch (err) {
      console.error("Ошибка при загрузке файла:", err);
      setMessage("❌ Upload failed. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-6 bg-white dark:bg-gray-800 p-6 shadow-lg rounded-md">
      <h2 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white">📄 Upload your Pitch Deck</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="file"
          accept=".pdf,.pptx"
          onChange={handleFileChange}
          className="w-full p-2 border rounded bg-white"
          required
        />

        <button
          type="submit"
          disabled={isUploading}
          className={`w-full px-4 py-2 rounded ${
            isUploading ? "bg-gray-400" : "bg-green-500 hover:bg-green-600"
          } text-white transition`}
        >
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </form>

      {file && <p className="mt-4 text-center text-sm text-gray-700">📎 Selected file: {file.name}</p>}
      {message && <p className="mt-2 text-center font-semibold text-blue-700">{message}</p>}
    </div>
  );
};

export default UploadPitchDeck;
