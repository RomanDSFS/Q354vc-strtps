
"use client";
import React from "react";
import Link from "next/link";

const Sidebar = () => {
  return (
    <div className="w-2 h-screen bg-gray-800 text-white p-4 fixed z-50">
      <h2 className="text-2xl font-bold mb-5">APP_5</h2>
      <ul className="space-y-4">
        
        <li><Link href="/"><span className="hover:text-blue-400"></span></Link></li>
        <li><Link href="/startups"><span className="hover:text-blue-400"></span></Link></li>
        <li><Link href="/investors"><span className="hover:text-blue-400"></span></Link></li>
        <li><Link href="/settings"><span className="hover:text-blue-400"></span></Link></li>

      </ul>
    </div>
  );
};

export default Sidebar;
