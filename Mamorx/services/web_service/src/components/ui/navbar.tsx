"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  const navLinks = [
    { href: "/", label: "Home" },
    { href: "/paper", label: "Paper" },
    { href: "/code", label: "Code" },
    { href: "/about", label: "About" },
  ];

  return (
    <nav className="bg-gray-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link
          href="/"
          className={`text-lg font-bold transition-colors ${
            pathname === "/" ? "text-blue-400" : "hover:text-blue-300"
          }`}
        >
          MAMORX
        </Link>
        <div className="flex gap-6">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`transition-colors ${
                pathname === link.href
                  ? "text-blue-400 font-medium"
                  : "hover:text-blue-300"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
