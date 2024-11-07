import PDFReviewerForm from "@/components/forms/pdf_reviewer";
import Navbar from "@/components/ui/navbar";
import Footer from "@/components/ui/footer";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8 text-center">
          MAMORX: Multi-agent Multi-Modal Scientific Review Generation
        </h1>
        <div className="max-w-3xl mx-auto">
          <PDFReviewerForm />
        </div>
      </main>
      <Footer />
    </div>
  );
}
