import type { Metadata } from "next";
import Navbar from "@/components/ui/navbar";
import Footer from "@/components/ui/footer";

export const metadata: Metadata = {
  title: "MAMORX Paper",
  description:
    "MAMORX: Multi-agent Multi-Modal Scientific Review Generation with External Knowledge",
};

export default async function PaperPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        <article className="prose prose-slate max-w-4xl mx-auto">
          <h1 className="text-3xl font-serif mb-6">
            MAMORX: Multi-agent Multi-Modal Scientific Review Generation with
            External Knowledge
          </h1>

          <div className="bg-muted/50 p-6 rounded-lg mb-8">
            <h2 className="text-xl font-medium mb-2">Authors</h2>
            <div className="space-y-2">
              <p>
                Pawin Taechoyotin<sup>1</sup>, Guanchao Wang<sup>1</sup>, Tong
                Zeng<sup>2</sup>, Bradley Sides<sup>1</sup>, Daniel Acuna
                <sup>1</sup>
              </p>
              <p className="text-sm text-muted-foreground">
                <sup>1</sup>University of Colorado Boulder
                <br />
                <sup>2</sup>Virginia Tech
              </p>
              <p className="text-sm text-muted-foreground break-words">
                {"{"}pawin.taechoyotin,guanchao.wang,bradley.sides,daniel.acuna
                {"}"}@colorado.edu
                <br />
                tongzeng@vt.edu
              </p>
            </div>
          </div>

          <div className="bg-muted/50 p-6 rounded-lg mb-8">
            <h2 className="text-xl font-medium mb-2">Publication Venue</h2>
            <p>
              Accepted at the Workshop on Foundation Models for Science:
              Progress, Opportunities, and Challenges (FM4Science) at NeurIPS
              2024
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Vancouver, Canada • Meeting Room #202-204
            </p>
          </div>

          <div className="bg-secondary/50 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Abstract</h2>
            <p className="text-foreground/90">
              The deluge of scientific papers has made it challenging for researchers to throughly evaluate their own and others{"'"} ideas with regards to novelty and improvements. We propose MAMORX, an automated scientific review generation system that relies on multi-modal foundation models to address this challenge. MAMORX replicates key aspects of human review by integrating attention to text, figures, and citations, along with access to external knowledge sources. Compared to previous work, it takes advantage of large context windows to significantly reduce the number of agents and the processing time needed. The system relies on structured outputs and function calling to handle figures, evaluate novelty, and build general and domain-specific knowledge bases from external scholarly search systems. To test our method, we conducted an arena-style competition between several baselines and human reviews on diverse papers from general machine learning and NLP fields, calculating an Elo ratings on human preferences. MAMORX has a high win rate against human reviews and outperforms the next-best model, a multi-agent system. We share our system (the code for our system can be found at <a href="https://github.com/sciosci/mamorx-review-system" className="underline underline-offset-1">https://github.com/sciosci/mamorx-review-system</a> and an example implementation is running at <a href="https://rev0.ai" className="underline underline-offset-1">https://rev0.ai</a>), and discuss further applications of foundation models for scientific evaluation.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <span className="bg-secondary text-secondary-foreground text-sm px-3 py-1 rounded-full">
              Multi-agent systems
            </span>
            <span className="bg-secondary text-secondary-foreground text-sm px-3 py-1 rounded-full">
              Multi-modal Foundation Models
            </span>
            <span className="bg-secondary text-secondary-foreground text-sm px-3 py-1 rounded-full">
              Scientific review generation
            </span>
          </div>

          <div className="pt-8">
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
        </article>
      </main>
      <Footer />
    </div>
  );
}
