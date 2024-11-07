import type { Metadata } from "next";
import Navbar from "@/components/ui/navbar";
import Footer from "@/components/ui/footer";

export const metadata: Metadata = {
  title: "About MAMORX",
  description: "About the MAMORX project and team",
};

export default async function AboutPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">About MAMORX</h1>

          <div className="prose prose-lg max-w-none space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-semibold mb-4">
                    Project Overview
                  </h2>
                  <p className="text-gray-700">
                    MAMORX is an innovative AI system designed to enhance the
                    quality of scientific reviews by leveraging multi-agent and
                    multi-modal analysis. Our goal is to assist researchers in
                    navigating the vast amount of scientific literature and
                    provide high-quality reviews efficiently.
                  </p>
                </div>

                <div className="bg-blue-50 p-6 rounded-lg">
                  <h2 className="text-xl font-semibold mb-4">Research Lab</h2>
                  <p className="text-gray-700">
                    MAMORX is developed at the Science of Science and
                    Computational Discovery Laboratory at the University of
                    Colorado Boulder. Our lab focuses on using computational
                    methods to understand and improve the scientific process.
                  </p>
                  <div className="mt-4">
                    <a
                      href="https://scienceofscience.org"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      Visit Lab Website
                    </a>
                  </div>
                </div>

                <div className="bg-gray-50 p-6 rounded-lg">
                  <h2 className="text-xl font-semibold mb-4">Key Features</h2>
                  <ul className="space-y-2 text-gray-700">
                    <li>• Multi-modal analysis of scientific papers</li>
                    <li>• Integration with external knowledge sources</li>
                    <li>• Advanced multi-agent system architecture</li>
                    <li>• Structured output generation</li>
                  </ul>
                </div>

                <div className="flex justify-center gap-4">
                  <a
                    href="https://anonymous.4open.science/r/MAMORX-BD44"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                  >
                    Project Page
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
