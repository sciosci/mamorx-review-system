import type { Metadata } from "next";
import Navbar from "@/components/ui/navbar";
import Footer from "@/components/ui/footer";
import { Button } from "@/components/ui/button";
import PDFReviewerForm from "@/components/forms/pdf_reviewer";

export const metadata: Metadata = {
  title: "MAMORX Demo",
  description: "Try MAMORX's AI-powered scientific review generation",
};

export default function DemoPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">Interactive Demo</h1>

          <div className="prose prose-lg max-w-none space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-semibold mb-4">About MAMORX</h2>
                  <p className="text-muted-foreground">
                    MAMORX is a state-of-the-art scientific review generation
                    system that leverages multi-modal foundation models and
                    external knowledge sources. Our system achieves a 93% win
                    rate against human reviews in direct comparisons, setting a
                    new standard for automated scientific review.
                  </p>
                </div>

                <div className="flex justify-center gap-4">
                  <Button asChild variant="outline">
                    <a href="/paper">Read Our Research Paper</a>
                  </Button>
                </div>

                <div className="bg-secondary/50 p-6 rounded-lg">
                  <h2 className="text-xl font-semibold mb-4">
                    Try It Yourself
                  </h2>
                  <PDFReviewerForm />
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
