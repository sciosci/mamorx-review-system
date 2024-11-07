import PDFReviewerForm from "@/components/forms/pdf_reviewer";
import Navbar from "@/components/ui/navbar";
import Footer from "@/components/ui/footer";

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

          <div className="bg-card rounded-xl shadow-md p-8 border border-border/50">
            <PDFReviewerForm />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
