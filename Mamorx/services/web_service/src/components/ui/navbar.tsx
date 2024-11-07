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
    <nav className="bg-primary text-primary-foreground p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link
          href="/"
          className={`text-lg font-bold transition-colors ${
            pathname === "/"
              ? "text-white underline decoration-2 underline-offset-4"
              : "text-primary-foreground/80 hover:text-primary-foreground"
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
                  ? "text-white font-medium underline decoration-2 underline-offset-4"
                  : "text-primary-foreground/80 hover:text-primary-foreground"
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
