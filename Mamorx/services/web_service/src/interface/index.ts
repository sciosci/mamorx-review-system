export interface IReviewResult {
    review_content: string,
    time_elapsed: number,
    novelty_assessment: string,
    figure_critic_assessment: string
};

export interface IPaperReviews {
    paper_id: string,
    authors: string,
    title: string,
    pdf_url: string,
    barebones: IReviewResult,
    liangetal: IReviewResult,
    multiagent: IReviewResult,
    mamorx: IReviewResult
};

export interface IReviewJob {
    id: string,
    status: "Queued" | "In-progress" | "Completed" | "Expired" | "Error",
    filename: string,
    review_type: "barebones" | "liangetal" | "multiagent" | "mamorx"
    result: IReviewResult | null | undefined
}

export interface ISessionJobs {
    count: number,
    jobs: IReviewJob[]
}

export interface IRateLimitState {
    remainingUserSubmissions: number;
    remainingTotalSubmissions: number;
    nextResetTime: string | null;
}