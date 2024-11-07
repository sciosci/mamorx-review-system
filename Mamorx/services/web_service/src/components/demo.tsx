import React from "react";

export default function Demo() {
  return (
    <div className="bg-gray-100 p-4 rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-2">AI Demo Section</h2>
      <p className="mb-4">
        Explore the capabilities of AI through our interactive demo.
      </p>
      <p>
        For more information, visit our{" "}
        <a href="https://anonymous.4open.science/r/MAMORX-BD44">
          MAMORX project page
        </a>
        .
      </p>
      <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        Start Demo
      </button>
    </div>
  );
}
