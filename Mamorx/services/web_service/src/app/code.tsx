import React from "react";
import Navbar from "@/components/ui/navbar";

export default function Code() {
  return (
    <div>
      <Navbar />
      <div className="p-4">
        <h1 className="text-3xl font-bold mb-4">Code Repository</h1>
        <p>
          Explore the source code for MAMORX and its components. You can find
          the code on our{" "}
          <a href="https://github.com/your-repo-link">GitHub repository</a>.
        </p>
        <p>
          The code is organized into various components, each serving a specific
          purpose in the MAMORX system.
        </p>
      </div>
    </div>
  );
}
