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
import { Card } from "@/components/ui/card";
import { SAMPLE_REVIEWS } from "@/data/sample_reviews";
import { ReviewResult } from "@/interface";

const FormSchema = z.object({
  review_type: z.string({
    required_error: "Please select a review source.",
  }),
});

interface RateLimitState {
  remainingUserSubmissions: number;
  remainingTotalSubmissions: number;
  nextResetTime: string | null;
}

export default function PDFReviewerForm() {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });
  const [inputFile, setInputFile] = React.useState<File>();
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showModal, setShowModal] = useState(false);
  const [pendingSubmission, setPendingSubmission] = useState<z.infer<
    typeof FormSchema
  > | null>(null);
  const [rateLimitInfo, setRateLimitInfo] = useState<RateLimitState>({
    remainingUserSubmissions: 3,
    remainingTotalSubmissions: 500,
    nextResetTime: null,
  });
  const [articleSource, setArticleSource] = React.useState<"Sample" | "Upload">("Sample");
  const [sampleArticleIndex, setSampleArticleIndex] = React.useState<number>(-1);
  const [reviewResult, setReviewResult] = React.useState<ReviewResult | undefined>(undefined);
  const [errorMessage, setErrorMessage] = React.useState<string>("");

  async function fetchRateLimitInfo() {
    try {
      const res = await axios.get("/api/generate-review");
      if (res.headers["x-ratelimit-remaining-user"]) {
        setRateLimitInfo({
          remainingUserSubmissions: parseInt(
            res.headers["x-ratelimit-remaining-user"]
          ),
          remainingTotalSubmissions: parseInt(
            res.headers["x-ratelimit-remaining-total"]
          ),
          nextResetTime: res.headers["x-ratelimit-reset"],
        });
      }
    } catch (error) {
      console.error("Error fetching rate limit info:", error);
    }
  }

  React.useEffect(() => {
    fetchRateLimitInfo();
  }, []);

  function handlePDFChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target?.files?.[0]) {
      const file = e.target.files[0];
      setInputFile(file);
    }
    setArticleSource("Upload");
    setSampleArticleIndex(-1);
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

      if (res.headers["x-ratelimit-remaining-user"]) {
        setRateLimitInfo({
          remainingUserSubmissions: parseInt(
            res.headers["x-ratelimit-remaining-user"]
          ),
          remainingTotalSubmissions: parseInt(
            res.headers["x-ratelimit-remaining-total"]
          ),
          nextResetTime: res.headers["x-ratelimit-reset"],
        });
      }

      setReviewResult(res.data);
      setErrorMessage("");
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 429) {
        setReviewResult(
          undefined
        );
        setErrorMessage(
          error.response.data.message ||
          "You've reached the maximum number of submissions for today. Please try again tomorrow."
        )
      } else {
        setReviewResult(undefined);
        setErrorMessage("Error submitting form.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    if (articleSource == "Upload") {
      setPendingSubmission(data);
      setShowModal(true);
    }
    else {
      if (data.review_type == "barebones") {
        setReviewResult(SAMPLE_REVIEWS[sampleArticleIndex].barebones);
      }
      else if (data.review_type == "liangetal") {
        setReviewResult(SAMPLE_REVIEWS[sampleArticleIndex].liangetal);
      }
      else if (data.review_type == "multiagent") {
        setReviewResult(SAMPLE_REVIEWS[sampleArticleIndex].multiagent);
      }
      else if (data.review_type == "mamorx") {
        setReviewResult(SAMPLE_REVIEWS[sampleArticleIndex].mamorx);
      }
      else {
        setReviewResult(undefined);
        alert("Unknown review type");
      }

    }
  }

  async function handleConfirmedSubmit() {
    if (pendingSubmission) {
      await submitFormToServer(pendingSubmission.review_type);
      setPendingSubmission(null);
    }
  }

  function handleSelectSampleArticle(index: number) {
    setArticleSource("Sample");
    setSampleArticleIndex(index);
  }

  function renderSampleArticleOptions() {
    return SAMPLE_REVIEWS.map((article, index) => {
      return (
        <Card className={`mt-2 mb-2 cursor-pointer ${sampleArticleIndex == index ? "border-blue-500 border-2" : ""}`} key={article.paper_id} onClick={() => { handleSelectSampleArticle(index) }}>
          <h4 className="text-3l">{article.title}</h4>
        </Card>
      );
    })
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <div className="grid grid-cols-12">
          <Card className="col-span-5 justify-items-center">
            <p className="text-muted-foreground m-2">
              Try out the reviews from 3 of
              our sample scientifc papers
            </p>
            {renderSampleArticleOptions()}
          </Card>
          <div className="col-span-2 content-center text-center">OR</div>
          <Card className={`col-span-5 justify-items-center ${sampleArticleIndex == -1 ? "border-blue-500 border-2" : ""}`}>
            <p className="text-muted-foreground m-2">
              Upload your scientific paper and select a review type to generate an
              AI-powered comprehensive review.
            </p>
            <div className="space-y-4 justify-items-center">
              <Label htmlFor="file" className="text-lg">
                Upload Paper
              </Label>
              <Input
                id="pdf_file"
                type="file"
                accept=".pdf"
                onChange={handlePDFChange}
                className="cursor-pointer"
              />
            </div>
          </Card>
        </div>
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

          <div className="text-sm text-muted-foreground mb-2">
            {rateLimitInfo.remainingUserSubmissions > 0
              ? `${rateLimitInfo.remainingUserSubmissions} submissions remaining today`
              : `Daily limit reached. Next reset: ${new Date(
                rateLimitInfo.nextResetTime!
              ).toLocaleString()}`}
          </div>

          <Button
            type="submit"
            disabled={isLoading || rateLimitInfo.remainingUserSubmissions === 0}
            className="w-full py-6 text-lg"
          >
            {isLoading
              ? "Generating Review..."
              : rateLimitInfo.remainingUserSubmissions === 0
                ? "Daily Limit Reached"
                : "Generate Review"}
          </Button>
        </form>
      </Form>

      <ConfirmationModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onConfirm={handleConfirmedSubmit}
      />

      {(reviewResult || errorMessage) && (
        <div className="mt-8 p-6 bg-secondary rounded-lg">
          <h3 className="text-xl font-semibold mb-4">Generated Review</h3>
          <div className="prose max-w-none whitespace-pre-wrap">{
            (reviewResult) ? reviewResult.review_content : errorMessage
          }</div>
        </div>
      )}
    </div>
  );
}
