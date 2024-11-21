"use client";
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
import { SAMPLE_REVIEWS } from "@/data/sample_reviews";
import { IReviewResult, ISessionJobs, IRateLimitState } from "@/interface";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { ConfirmationModal } from "@/components/ui/modal";
import { ArrowUpRight, Users, Loader2 } from "lucide-react";
import { formatDuration, getReviewDuration, isStringInArray } from "@/lib";
import { REVIEW_TYPE_OPTIONS } from "@/data";
import { TReviewType } from "@/types";
import {
  getSessionJobs,
  getRateLimitInfo,
  submitReview
} from "@/services/mamorx";

const FormSchema = z.object({
  review_type: z.string({
    required_error: "Please select a review source.",
  }),
  pdf_file: z.any().optional(),
});

export default function PDFReviewerForm() {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      pdf_file: undefined,
    },
  });
  const [inputFile, setInputFile] = React.useState<File>();
  const [showModal, setShowModal] = React.useState(false);
  const [pendingSubmission, setPendingSubmission] = React.useState<z.infer<
    typeof FormSchema
  > | null>(null);
  const [rateLimitInfo, setRateLimitInfo] = React.useState<IRateLimitState>({
    remainingUserSubmissions: 3,
    remainingTotalSubmissions: 500,
    nextResetTime: null,
  });
  const [articleSource, setArticleSource] = React.useState<"Sample" | "Upload">(
    "Sample"
  );
  const [sampleArticleIndex, setSampleArticleIndex] = React.useState<number>(0);
  const [reviewResult, setReviewResult] = React.useState<
    IReviewResult | undefined
  >(undefined);
  const [errorMessage, setErrorMessage] = React.useState<string>("");
  const [sessionJobs, setSessionJobs] = React.useState<ISessionJobs | undefined>();
  const [recentReviewIndex, setRecentReviewIndex] = React.useState<number>(-1);
  const resultRef = React.useRef<HTMLDivElement>(null);
  const [pendingReview, setPendingReview] = React.useState<boolean>(false);
  const [lastCheckedDate, setLastCheckedDate] = React.useState<Date>(new Date());

  React.useEffect(() => {
    const reviewStatuses = sessionJobs?.jobs.map(({ status }) => status) || [];
    if (isStringInArray(reviewStatuses, "Queued") || isStringInArray(reviewStatuses, "In-progress")) {
      setPendingReview(true);
    }
    else {
      setPendingReview(false);
    }
  }, [sessionJobs]);

  React.useEffect(() => {
    let intervalId: NodeJS.Timeout;
    if (pendingReview) {
      intervalId = setInterval(() => fetchSessionJobs(), 10000);
    }

    return () => clearInterval(intervalId);
  }, [pendingReview]);

  async function fetchSessionJobs() {
    const res = await getSessionJobs();
    if (res.success && res.data) {
      setSessionJobs(res.data);
      setLastCheckedDate(new Date());
    }
  }

  async function fetchRateLimitInfo() {
    const res = await getRateLimitInfo();
    if (res.success && res.data) {
      setRateLimitInfo(res.data);
    }
  }

  React.useEffect(() => {
    fetchSessionJobs();
    fetchRateLimitInfo();
  }, []);

  function handlePDFChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target?.files?.[0]) {
      const file = e.target.files[0];
      setInputFile(file);
      form.setValue("pdf_file", file);
    } else {
      setInputFile(undefined);
      form.setValue("pdf_file", undefined);
    }
    setArticleSource("Upload");
    setSampleArticleIndex(-1);
  }

  async function submitFormToServer(reviewType: TReviewType) {
    const res = await submitReview(inputFile as Blob, reviewType);
    if (res.success && res.data) {
      setRateLimitInfo(res.data.rate_limit_info);
      fetchSessionJobs();
      setErrorMessage("");
    }
    else {
      setReviewResult(undefined);
      setErrorMessage(res.msg);
    }
  }

  function onSubmit(data: z.infer<typeof FormSchema>) {
    if (articleSource === "Upload") {
      if (!inputFile) {
        form.setError("pdf_file", {
          type: "required",
          message: "Please select a PDF file",
        });
        return;
      }

      // Only check rate limit for uploads
      if (rateLimitInfo.remainingUserSubmissions === 0) {
        setErrorMessage(
          "You've reached the maximum number of submissions for today. Please try again tomorrow."
        );
        return;
      }

      setPendingSubmission(data);
      setShowModal(true);
    } else {
      // Sample reviews should always work regardless of rate limit
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
      await submitFormToServer(pendingSubmission.review_type as TReviewType);
      setPendingSubmission(null);
    }
  }

  function handleSelectSampleArticle(index: number) {
    if (articleSource === "Sample" && sampleArticleIndex == index) {
      resultRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
    else {
      setArticleSource("Sample");
      setSampleArticleIndex(index);
    }
  }

  function handleSelectRecentReview(index: number) {
    if (sessionJobs?.jobs[index].status == "Completed") {
      if (index == recentReviewIndex) {
        resultRef.current?.scrollIntoView({ behavior: 'smooth' });
      }
      else {
        setArticleSource("Upload");
        setRecentReviewIndex(index);
        setReviewResult(sessionJobs?.jobs[index].result || undefined);
      }
    }
    else {
      console.error("Selected submission has either expired or hasn't been completed.");
    }
  }

  function renderSessionJobs() {
    return (
      <Carousel className="w-full max-w-xl mt-10" orientation="vertical">
        <CarouselContent className="content-center -mt-1 h-[300px]">
          {sessionJobs?.jobs.map((job, index) => {
            return (
              <CarouselItem
                key={job.id}
                className="content-center md:basis-1/2 lg:basis-1/3"
              >
                <Card
                  className={`mt-2 mb-2 content-center justify-items-center cursor-pointer ${recentReviewIndex == index
                    ? "border-blue-500 border-2"
                    : ""
                    }`}
                  onClick={() => {
                    handleSelectRecentReview(index);
                  }}
                >
                  <CardHeader className="space-y-4">
                    <div className="flex items-start justify-between gap-4">
                      <CardTitle className="text-md font-bold leading-tight break-all">
                        {`${index + 1}. ${job.filename} [${job.review_type}] (${job.status})`}
                      </CardTitle>
                    </div>
                  </CardHeader>
                </Card>
              </CarouselItem>
            );
          })}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    );
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
                  className={`mt-2 mb-2 content-center justify-items-center cursor-pointer ${sampleArticleIndex == index
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
                Try out the review on your own scientific paper.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="space-y-4 justify-items-center">
                <Input
                  id="pdf_file"
                  type="file"
                  accept=".pdf"
                  onChange={handlePDFChange}
                  className="cursor-pointer"
                />
              </div>
            </CardContent>
            <CardFooter>
              <Card className="w-full">
                <CardHeader>
                  <CardTitle>Recent Reviews</CardTitle>
                  <CardDescription>
                    List of result for past submissions (last checked at {lastCheckedDate.toLocaleString()})
                  </CardDescription>
                  <Button
                    className="w-full text-lg row-span-1"
                    onClick={fetchSessionJobs}
                  >
                    Reload Review Status
                    {pendingReview && <Loader2 className="animate-spin" />}
                  </Button>
                </CardHeader>
                <CardContent className="space-y-2">
                  {sessionJobs?.jobs.length !== 0 ? renderSessionJobs() : (
                    <p className="text-md">
                      No recent submissions
                    </p>
                  )}
                </CardContent>
                <CardFooter>
                </CardFooter>
              </Card>
            </CardFooter>
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
            name="pdf_file"
            render={({ field }) => (
              <FormItem className="hidden">
                <FormControl>
                  <Input
                    type="text"
                    {...field}
                    value={inputFile?.name || ""}
                    onChange={() => { }}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

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
                    {REVIEW_TYPE_OPTIONS.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label} (approximately{" "}
                        {formatDuration(getReviewDuration(type.value))})
                      </SelectItem>
                    ))}
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
            disabled={
              (articleSource === "Upload" &&
                (rateLimitInfo.remainingUserSubmissions === 0 || !inputFile)) ||
              !form.getValues("review_type")
            }
            className="w-full py-6 text-lg"
          >
            {articleSource === "Upload" &&
              rateLimitInfo.remainingUserSubmissions === 0
              ? "Daily Upload Limit Reached"
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
        <div className="mt-8 p-6 bg-secondary rounded-lg" ref={resultRef}>
          <h3 className="text-xl font-semibold mb-4">Generated Review</h3>
          <div className="prose max-w-none whitespace-pre-wrap">
            {reviewResult ? renderReviewTabs() : errorMessage}
          </div>
        </div>
      )}
    </div>
  );
}
