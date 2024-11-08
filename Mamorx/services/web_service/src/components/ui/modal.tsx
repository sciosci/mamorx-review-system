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
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-background rounded-lg p-4 max-w-4xl w-full relative border shadow-md">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="space-y-4">
          <h3 className="text-lg font-serif font-medium text-primary">
            Important Notice
          </h3>

          <div className="space-y-4">
            <div className="bg-accent/50 p-4 rounded-lg border border-accent">
              <h4 className="font-serif font-medium mb-2 text-foreground text-sm">
                Privacy Notice
              </h4>
              <p className="text-foreground/90 leading-relaxed text-sm">
                While we are careful to delete uploaded PDFs after processing,
                we cannot provide absolute guarantees about data handling.
                Please ensure you have the right to share any uploaded
                documents.
              </p>
            </div>

            <div className="bg-accent/50 p-4 rounded-lg border border-accent">
              <h4 className="font-serif font-medium mb-2 text-foreground text-sm">
                Watermarking
              </h4>
              <p className="text-foreground/90 leading-relaxed text-sm">
                All generated reviews will contain watermarks to ensure they can
                be detected if used as actual reviews. These reviews are
                intended for research and demonstration purposes only.
              </p>
            </div>

            <div className="bg-secondary p-4 rounded-lg border border-border">
              <h4 className="font-serif font-medium mb-2 text-sm">Citation</h4>
              <p className="text-secondary-foreground text-sm">
                If you use MAMORX in your research, please cite our work:
              </p>
              <div className="bg-muted/70 p-3 rounded-md mt-2 font-mono text-xs">
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
                className="inline-flex items-center mt-2 text-primary hover:text-primary/90 transition-colors text-sm"
              >
                Download BibTeX
              </a>
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-4">
            <button
              onClick={onClose}
              className="px-4 py-2 text-muted-foreground hover:text-foreground transition-colors font-serif text-sm"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors font-serif text-sm"
            >
              I Understand and Agree
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
