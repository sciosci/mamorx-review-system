export default function Footer() {
  return (
    <footer className="bg-primary text-primary-foreground py-6 mt-auto">
      <div className="container mx-auto text-center space-y-2">
        <p className="mb-2">&copy; 2024 MAMORX. All rights reserved.</p>
        <p className="text-sm text-primary-foreground/80">
          Developed at the{" "}
          <a
            href="https://scienceofscience.org"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-accent-foreground underline"
          >
            Science of Science and Computational Discovery Lab
          </a>
        </p>
        <p className="text-sm text-primary-foreground/80">
          University of Colorado Boulder
        </p>
      </div>
    </footer>
  );
}
