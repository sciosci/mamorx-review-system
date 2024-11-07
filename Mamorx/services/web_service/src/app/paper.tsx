import React from "react";
import Navbar from "@/components/ui/navbar";

export default function Paper() {
  return (
    <div>
      <Navbar />
      <div className="p-4">
        <h1 className="text-3xl font-bold mb-4">MAMORX Paper</h1>
        <p>
          MAMORX is an AI system that improves scientific review quality by
          integrating multi-agent, multi-modal analysis with external knowledge
          sources.
        </p>
        <p>Published: 11 Oct 2024, Last Modified: 02 Nov 2024</p>
        <p>
          Keywords: Multi-agent systems, Multi-modal Foundation Models,
          Scientific review generation
        </p>
        <p>
          For more details, refer to the full paper available on our{" "}
          <a href="https://anonymous.4open.science/r/MAMORX-BD44">
            project page
          </a>
          .
        </p>
      </div>
    </div>
  );
}
