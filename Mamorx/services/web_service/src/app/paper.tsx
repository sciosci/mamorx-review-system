import React from "react";
import Navbar from "@/components/ui/navbar";

export default function Paper() {
  return (
    <div>
      <Navbar />
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <article className="prose prose-slate max-w-none">
          <h1 className="text-3xl font-serif mb-6">
            MAMORX: Multi-agent Multi-Modal Scientific Review Generation
          </h1>

          <div className="bg-muted/50 p-6 rounded-lg mb-8">
            <h2 className="text-xl font-medium mb-2">Publication Venue</h2>
            <p>
              Accepted at the Workshop on Foundation Models for Science:
              Progress, Opportunities, and Challenges (FM4Science) at NeurIPS
              2024
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              December 15, 2024 • Vancouver, Canada • Meeting Room #202-204
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="text-xl font-medium">Abstract</h2>
            <p className="text-gray-700">
              This paper presents MAMORX, a system that integrates multi-agent
              and multi-modal analysis with external knowledge sources for
              scientific review generation. We demonstrate the system&apos;s
              effectiveness through comprehensive evaluations and user studies.
            </p>

            <div className="flex flex-col gap-2 text-sm text-muted-foreground">
              <p>
                <strong>Keywords:</strong> Multi-agent systems, Multi-modal
                Foundation Models, Scientific review generation
              </p>
              <p>
                <strong>Published:</strong> October 11, 2024
              </p>
              <p>
                <strong>Last Modified:</strong> November 2, 2024
              </p>
            </div>

            <div className="pt-4">
              <h2 className="text-xl font-medium mb-2">Resources</h2>
              <ul className="list-disc pl-5 space-y-2">
                <li>
                  <a
                    href="https://anonymous.4open.science/r/MAMORX-BD44"
                    className="text-primary hover:underline"
                  >
                    Project Repository
                  </a>
                </li>
                <li>
                  <a
                    href="https://neurips.cc/virtual/2024/workshop/84714"
                    className="text-primary hover:underline"
                  >
                    Workshop Page
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </article>
      </div>
    </div>
  );
}
