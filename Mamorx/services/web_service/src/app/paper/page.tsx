import type { Metadata } from "next";
import Navbar from "@/components/ui/navbar";
import Footer from "@/components/ui/footer";

export const metadata: Metadata = {
  title: "MAMORX Paper",
  description: "MAMORX: Multi-agent Multi-Modal Scientific Review Generation",
};

export default async function PaperPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">MAMORX Paper</h1>

          <div className="prose prose-lg max-w-none space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <p className="text-lg mb-6">
                MAMORX is an AI system that improves scientific review quality
                by integrating multi-agent, multi-modal analysis with external
                knowledge sources.
              </p>

              <div className="space-y-4">
                <div className="border-l-4 border-blue-500 pl-4">
                  <p className="text-sm text-gray-600">
                    Published: 11 Oct 2024
                  </p>
                  <p className="text-sm text-gray-600">
                    Last Modified: 02 Nov 2024
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  <span className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                    Multi-agent systems
                  </span>
                  <span className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                    Multi-modal Foundation Models
                  </span>
                  <span className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">
                    Scientific review generation
                  </span>
                </div>

                <div className="bg-gray-50 p-6 rounded-lg">
                  <h2 className="text-xl font-semibold mb-4">Abstract</h2>
                  <p className="text-gray-700">
                    The deluge of scientific papers has made it challenging for
                    researchers to thoroughly engage with the expanding
                    literature. We propose MAMORX, a new automated scientific
                    review generation system that relies on multi-modal
                    foundation models to address this challenge. MAMORX
                    replicates key aspects of human review by integrating
                    attention to text, figures, and citations, along with access
                    to external knowledge sources.
                  </p>
                </div>

                <div className="flex justify-center">
                  <a
                    href="https://anonymous.4open.science/r/MAMORX-BD44"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                  >
                    Read Full Paper
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
