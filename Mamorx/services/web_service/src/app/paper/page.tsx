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
                Guanchao Wang<sup>1</sup>, Pawin Taechoyotin<sup>1</sup>, Tong
                Zeng<sup>2</sup>, Bradley Sides<sup>1</sup>, Daniel Acuna
                <sup>1</sup>
              </p>
              <p className="text-sm text-muted-foreground">
                <sup>1</sup>University of Colorado Boulder
                <br />
                <sup>2</sup>Virginia Tech
              </p>
              <p className="text-sm text-muted-foreground break-words">
                {"{"}guanchao.wang,pawin.taechoyotin,bradley.sides,daniel.acuna
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
              The deluge of scientific papers has made it challenging for
              researchers to thoroughly engage with the expanding literature. We
              propose MAMORX, a new automated scientific review generation
              system that relies on multi-modal foundation models to address
              this challenge. MAMORX replicates key aspects of human review by
              integrating attention to text, figures, and citations, along with
              access to external knowledge sources. Compared to previous work,
              it takes advantage of large context windows to significantly
              reduce the number of agents and the processing time needed. The
              system relies on structured outputs and function calling to
              process figures, evaluate novelty, and build general and
              domain-specific knowledge bases from external scholarly search. To
              test our system, we conducted an arena-style competition between
              several baselines and human reviews on diverse papers from general
              machine learning and NLP fields, calculating an Elo rating for
              each model based on human preferences. MAMORX has an estimated win
              rate of 93% against human reviews and outperforms the next-best
              model, a multi-agent baseline system, losing only 12% of the time
              and never losing against other prominent models. We share our
              system, and discuss further applications of foundation models,
              especially multi-modal ones, for scientific evaluation.
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
