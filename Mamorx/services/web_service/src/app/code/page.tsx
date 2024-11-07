import type { Metadata } from "next";
import Navbar from "@/components/ui/navbar";
import Footer from "@/components/ui/footer";
import { Button } from "@/components/ui/button";

export const metadata: Metadata = {
  title: "MAMORX Code",
  description: "Code repository for MAMORX project",
};

export default async function CodePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">Code Repository</h1>

          <div className="prose prose-lg max-w-none space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <p className="text-lg mb-6">
                Explore the source code for MAMORX and its components. Our code
                is open-source and available for research purposes.
              </p>

              <div className="space-y-6">
                <div className="bg-gray-50 p-6 rounded-lg">
                  <h2 className="text-xl font-semibold mb-4">
                    Repository Structure
                  </h2>
                  <ul className="space-y-2 text-gray-700">
                    <li>• Multi-agent System Implementation</li>
                    <li>• Multi-modal Analysis Components</li>
                    <li>• External Knowledge Integration</li>
                    <li>• Review Generation Pipeline</li>
                  </ul>
                </div>

                <div className="flex justify-center">
                  <Button asChild size="lg">
                    <a
                      href="https://anonymous.4open.science/r/MAMORX-BD44"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Access Repository
                    </a>
                  </Button>
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
