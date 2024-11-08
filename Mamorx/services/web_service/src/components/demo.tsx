import React from "react";

export default function Demo() {
  return (
    <div className="bg-card p-4 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-2">AI Demo Section</h2>
      <p className="mb-4 text-card-foreground">
        Explore the capabilities of AI through our interactive demo.
      </p>
      <p className="text-card-foreground">
        For more information, visit our{" "}
        <a
          href="https://anonymous.4open.science/r/MAMORX-BD44"
          className="text-primary hover:text-primary/90 underline"
        >
          MAMORX project page
        </a>
        .
      </p>
      <button className="bg-primary text-primary-foreground px-4 py-2 rounded hover:bg-primary/90">
        Start Demo
      </button>
    </div>
  );
}
