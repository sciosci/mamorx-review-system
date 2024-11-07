"use client";
import axios from "axios";
import React from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { ConfirmationModal } from "@/components/ui/modal";

const FormSchema = z.object({
  review_type: z.string({
    required_error: "Please select a review source.",
  }),
});

export default function PDFReviewerForm() {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });
  const [inputFile, setInputFile] = React.useState<File>();
  const [responseMessage, setResponseMessage] = React.useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showModal, setShowModal] = useState(false);
  const [pendingSubmission, setPendingSubmission] = useState<z.infer<
    typeof FormSchema
  > | null>(null);

  function handlePDFChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target?.files?.[0]) {
      const file = e.target.files[0];
      setInputFile(file);
    }
  }

  async function submitFormToServer(review_type: string) {
    const headers = {
      "Content-Type": "multipart/form-data",
    };
    const formData = new FormData();
    formData.append("pdf_file", inputFile as Blob);
    formData.append("review_type", review_type);

    try {
      setIsLoading(true);
      const res = await axios.post("/api/generate-review", formData, {
        headers: headers,
      });

      setResponseMessage(res.data.review_content);
    } catch (error) {
      console.error("Error submitting form:", error);
      setResponseMessage("Error submitting form.");
    } finally {
      setIsLoading(false);
    }
  }

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    setPendingSubmission(data);
    setShowModal(true);
  }

  async function handleConfirmedSubmit() {
    if (pendingSubmission) {
      await submitFormToServer(pendingSubmission.review_type);
      setPendingSubmission(null);
    }
  }

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-lg p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-2">PDF Review Generator</h2>
        <p className="text-gray-600">
          Upload your scientific paper and select a review type to generate an
          AI-powered review.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormField
            control={form.control}
            name="review_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-lg">Review Type</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select a type of review" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="barebones">Barebones Review</SelectItem>
                    <SelectItem value="liangetal">
                      Liang et al. Style
                    </SelectItem>
                    <SelectItem value="multiagent">
                      Multi-agent Review
                    </SelectItem>
                    <SelectItem value="mamorx">MAMORX Review</SelectItem>
                  </SelectContent>
                </Select>
                <FormDescription>
                  Choose the review style that best suits your needs
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="space-y-4">
            <Label htmlFor="file" className="text-lg">
              Upload PDF
            </Label>
            <Input
              id="pdf_file"
              type="file"
              accept=".pdf"
              onChange={handlePDFChange}
              className="cursor-pointer"
            />
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full py-6 text-lg"
          >
            {isLoading ? "Generating Review..." : "Generate Review"}
          </Button>
        </form>
      </Form>

      <ConfirmationModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onConfirm={handleConfirmedSubmit}
      />

      {responseMessage && (
        <div className="mt-8 p-6 bg-gray-50 rounded-lg">
          <h3 className="text-xl font-semibold mb-4">Generated Review</h3>
          <div className="prose max-w-none">{responseMessage}</div>
        </div>
      )}
    </div>
  );
}
