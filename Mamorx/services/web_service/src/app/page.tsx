import PDFReviewerForm from "@/components/forms/pdf_reviewer";
import Navbar from "@/components/ui/navbar";
import Footer from "@/components/ui/footer";
import { FileText, Github } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto space-y-10">
          <h1 className="text-4xl font-serif font-medium text-center leading-tight">
            MAMORX: Multi-agent Multi-Modal Scientific Review Generation with
            External Knowledge
          </h1>

          <div className="bg-accent/50 p-8 rounded-lg border border-accent">
            <p className="text-lg text-center font-serif leading-relaxed">
              MAMORX is a scientific review system. Our system leverages
              multi-modal foundation models and external knowledge to provide
              comprehensive scientific paper analysis.
            </p>
          </div>

          <div className="flex justify-center gap-4">
            <a
              href="https://openreview.net/pdf?id=frvkE8rCfX"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium text-lg"
            >
              <FileText className="h-5 w-5" />
              Read the Paper
            </a>
            <a
              href="https://github.com/sciosci/mamorx-review-system"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium text-lg"
            >
              <Github className="h-5 w-5" />
              Code
            </a>
            <a
              href="https://forms.gle/198xkRZgkz6yCcqj8"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium text-lg"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-5 w-5"
              >
                <path d="M16 16v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h3" />
                <path d="M15 5h4v4" />
                <path d="m16 9-7 7" />
              </svg>
              Signup for Updates
            </a>
          </div>

          <div className="bg-card rounded-xl shadow-md p-8 border border-border/50">
            <PDFReviewerForm />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
