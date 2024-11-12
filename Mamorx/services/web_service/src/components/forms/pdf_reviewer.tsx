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
import { SAMPLE_REVIEWS } from "@/data/sample_reviews";
import { ReviewResult } from "@/interface";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { ScrollText, Users, MessageCircle, ArrowUpRight } from "lucide-react";

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
  const [articleSource, setArticleSource] = React.useState<"Sample" | "Upload">(
    "Sample"
  );
  const [sampleArticleIndex, setSampleArticleIndex] = React.useState<number>(0);
  const [reviewResult, setReviewResult] = React.useState<
    ReviewResult | undefined
  >(undefined);
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
        setReviewResult(undefined);
        setErrorMessage(
          error.response.data.message ||
            "You've reached the maximum number of submissions for today. Please try again tomorrow."
        );
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
    } else {
      if (data.review_type == "barebones") {
        setReviewResult(SAMPLE_REVIEWS[sampleArticleIndex].barebones);
      } else if (data.review_type == "liangetal") {
        setReviewResult(SAMPLE_REVIEWS[sampleArticleIndex].liangetal);
      } else if (data.review_type == "multiagent") {
        setReviewResult(SAMPLE_REVIEWS[sampleArticleIndex].multiagent);
      } else if (data.review_type == "mamorx") {
        setReviewResult(SAMPLE_REVIEWS[sampleArticleIndex].mamorx);
      } else {
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
    return (
      <Carousel className="w-full max-w-xl " orientation="vertical">
        <CarouselContent className="content-center">
          {SAMPLE_REVIEWS.map((article, index) => {
            return (
              <CarouselItem
                key={article.paper_id}
                className="content-center md:basis-1/2 lg:basis-1/3"
              >
                <Card
                  className={`mt-2 mb-2 content-center justify-items-center cursor-pointer ${
                    sampleArticleIndex == index
                      ? "border-blue-500 border-2"
                      : ""
                  }`}
                  onClick={() => {
                    handleSelectSampleArticle(index);
                  }}
                >
                  <CardHeader className="space-y-4">
                    <div className="flex items-start justify-between gap-4">
                      <CardTitle className="text-xl font-bold leading-tight">
                        {article.title}
                      </CardTitle>
                      <ArrowUpRight className="w-5 h-5 flex-shrink-0 text-gray-400" />
                    </div>

                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Users className="w-4 h-4" />
                      <span>{article.authors}</span>
                    </div>
                  </CardHeader>
                  <CardFooter className="break-all">
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">DOI: </span>
                      <span className="text-blue-600 hover:underline">
                        <a
                          href={article.pdf_url}
                          className="text-wrap underline underline-offset-1"
                        >
                          {article.pdf_url}
                        </a>
                      </span>
                    </div>
                  </CardFooter>
                </Card>
              </CarouselItem>
            );
          })}
        </CarouselContent>
      </Carousel>
    );
  }

  function renderReviewTabs() {
    return (
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="novelty">Novelty Assessment</TabsTrigger>
          <TabsTrigger value="figure">Figure Assessment</TabsTrigger>
        </TabsList>
        <TabsContent value="overview">
          <Card>
            <CardHeader>
              <CardTitle>Overview</CardTitle>
              <CardDescription>
                An overview regarding all aspects of the selected scientific
                paper.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="prose max-w-none whitespace-pre-wrap space-y-1">
                {reviewResult?.review_content}
              </div>
            </CardContent>
            <CardFooter></CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="novelty">
          <Card>
            <CardHeader>
              <CardTitle>Novelty Assessment</CardTitle>
              <CardDescription>
                An assessment regarding the novelty of the selected scientific
                paper based on previous work within our database.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="prose max-w-none whitespace-pre-wrap space-y-1">
                {reviewResult?.novelty_assessment ||
                  "No direct assessment of novelty was performed."}
              </div>
            </CardContent>
            <CardFooter></CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="figure">
          <Card>
            <CardHeader>
              <CardTitle>Figure Assessment</CardTitle>
              <CardDescription>
                An assessment regarding the clarity and consistency of figures
                in respect to the content of the selected scientific paper.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="prose max-w-none whitespace-pre-wrap space-y-1">
                {reviewResult?.figure_critic_assessment ||
                  "No direct assessment of the figures were performed."}
              </div>
            </CardContent>
            <CardFooter></CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    );
  }

  function renderPaperOptions() {
    return (
      <Tabs defaultValue="sample" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger
            value="sample"
            onClick={() => setArticleSource("Sample")}
          >
            Sample Papers
          </TabsTrigger>
          <TabsTrigger
            value="upload"
            onClick={() => setArticleSource("Upload")}
          >
            Upload Your Own
          </TabsTrigger>
        </TabsList>
        <TabsContent value="sample">
          <Card>
            <CardHeader>
              <CardTitle>Reviews from Sample Papers</CardTitle>
              <CardDescription>
                Try out the reviews from 3 of our sample scientific papers.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 justify-items-center">
              {renderSampleArticleOptions()}
            </CardContent>
            <CardFooter></CardFooter>
          </Card>
        </TabsContent>
        <TabsContent value="upload">
          <Card>
            <CardHeader>
              <CardTitle>Upload PDF</CardTitle>
              <CardDescription>
                Try out the review on your own scientifc paper.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="space-y-4 justify-items-center">
                {/* <Label htmlFor="file" className="text-lg">
                  Upload Paper
                </Label> */}
                <Input
                  id="pdf_file"
                  type="file"
                  accept=".pdf"
                  onChange={handlePDFChange}
                  className="cursor-pointer"
                />
              </div>
            </CardContent>
            <CardFooter></CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">{renderPaperOptions()}</div>

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
              : articleSource === "Sample"
              ? "Show Review"
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
          <div className="prose max-w-none whitespace-pre-wrap">
            {reviewResult ? renderReviewTabs() : errorMessage}
          </div>
        </div>
      )}
    </div>
  );
}
