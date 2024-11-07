"use client";
import React from "react";
import { X } from "lucide-react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function ConfirmationModal({ isOpen, onClose, onConfirm }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 max-w-2xl mx-4 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
        >
          <X className="h-6 w-6" />
        </button>

        <div className="space-y-6">
          <h3 className="text-2xl font-semibold">Important Notice</h3>

          <div className="space-y-4 text-gray-700">
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Privacy Notice</h4>
              <p>
                While we are careful to delete uploaded PDFs after processing,
                we cannot provide absolute guarantees about data handling.
                Please ensure you have the right to share any uploaded
                documents.
              </p>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Watermarking</h4>
              <p>
                All generated reviews will contain watermarks to ensure they can
                be detected if used as actual reviews. These reviews are
                intended for research and demonstration purposes only.
              </p>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Citation</h4>
              <p>If you use MAMORX in your research, please cite our work:</p>
              <div className="bg-gray-100 p-3 rounded mt-2 font-mono text-sm">
                @article{"{"}mamorx2024,
                <br />
                &nbsp;&nbsp;title={"{"}MAMORX: Multi-agent Multi-Modal
                Scientific Review Generation{"}"}, <br />
                &nbsp;&nbsp;author={"{"}Anonymous{"}"}, <br />
                &nbsp;&nbsp;year={"{"}2024{"}"}
                <br />
                {"}"}
              </div>
              <a
                href="/citation.bib"
                download
                className="inline-flex items-center mt-2 text-blue-600 hover:text-blue-800"
              >
                Download BibTeX
              </a>
            </div>
          </div>

          <div className="flex justify-end gap-4 mt-6">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              I Understand and Agree
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
