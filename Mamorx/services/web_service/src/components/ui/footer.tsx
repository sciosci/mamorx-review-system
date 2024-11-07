export default function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-6 mt-auto">
      <div className="container mx-auto text-center space-y-2">
        <p className="mb-2">&copy; 2024 MAMORX. All rights reserved.</p>
        <p className="text-sm text-gray-300">
          Developed at the{" "}
          <a
            href="https://scienceofscience.org"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-blue-300 underline"
          >
            Science of Science and Computational Discovery Lab
          </a>
        </p>
        <p className="text-sm text-gray-300">University of Colorado Boulder</p>
      </div>
    </footer>
  );
}
