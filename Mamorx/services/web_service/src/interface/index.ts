import {
    TReviewType,
    TReviewStatus
} from "@/types";

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
    status: TReviewStatus,
    filename: string,
    review_type: TReviewType,
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

export interface ISubmitReview {
    job: IReviewJob,
    rate_limit_info: IRateLimitState
}

export interface IResponse {
    success: boolean,
    data: ISessionJobs | IRateLimitState | ISubmitReview | null,
    msg: string
}

export interface ISessionJobsResponse extends IResponse {
    data: ISessionJobs | null
}

export interface IRateLimitInfoResponse extends IResponse {
    data: IRateLimitState | null
}

export interface ISubmitReviewResponse extends IResponse {
    data: ISubmitReview | null
}
