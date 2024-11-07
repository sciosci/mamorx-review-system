import type { Metadata } from "next";
import Navbar from "@/components/ui/navbar";
import Footer from "@/components/ui/footer";
import { Button } from "@/components/ui/button";

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

                <div className="bg-secondary p-6 rounded-lg">
                  <h2 className="text-xl font-semibold mb-4">Research Lab</h2>
                  <p className="text-secondary-foreground">
                    MAMORX is developed at the Science of Science and
                    Computational Discovery Laboratory at the University of
                    Colorado Boulder. Our lab focuses on using computational
                    methods to understand and improve the scientific process.
                  </p>
                </div>

                <div className="bg-primary/5 p-6 rounded-lg border border-primary/10">
                  <h2 className="text-xl font-semibold mb-4">Join Our Team</h2>
                  <p className="text-foreground/90 mb-4">
                    We are actively recruiting talented researchers and
                    engineers interested in AI, multi-agent systems, and
                    scientific discovery. If you&apos;re passionate about
                    advancing scientific research through AI, we&apos;d love to
                    hear from you.
                  </p>
                  <p className="text-foreground/90">
                    Visit our lab website to learn more about open positions and
                    how to apply.
                  </p>
                </div>

                <div className="flex justify-center gap-4">
                  <Button asChild size="lg">
                    <a
                      href="https://scienceofscience.org"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Visit Lab Website
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
