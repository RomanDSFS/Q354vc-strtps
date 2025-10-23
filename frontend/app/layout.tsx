import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import { AuthProvider } from "@/context/AuthContext"; // ✅ Подключаем контекст

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "APP_5",
  description: "Платформа для венчурных инвесторов и стартапов",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body className="flex">
        <AuthProvider> {/* ✅ Оборачиваем всё */}
          <Sidebar />
          <div className="w-full">
              <Navbar />      {/* 👈 теперь имеет доступ к useAuth() */}
              <main className="p-4">{children}</main>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
