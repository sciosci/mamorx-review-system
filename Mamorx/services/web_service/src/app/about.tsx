import React from "react";
import Navbar from "@/components/ui/navbar";

export default function About() {
  return (
    <div>
      <Navbar />
      <div className="p-4">
        <h1 className="text-3xl font-bold mb-4">About MAMORX</h1>
        <p>
          MAMORX is an innovative AI system designed to enhance the quality of
          scientific reviews by leveraging multi-agent and multi-modal analysis.
        </p>
        <p>
          Our goal is to assist researchers in navigating the vast amount of
          scientific literature and provide high-quality reviews efficiently.
        </p>
      </div>
    </div>
  );
}
