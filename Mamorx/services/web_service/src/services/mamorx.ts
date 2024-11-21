import axios from "axios";
import {
    TReviewType
} from "@/types";
import {
    ISessionJobsResponse,
    IRateLimitInfoResponse,
    ISubmitReviewResponse
} from "@/interface";

export async function getSessionJobs(): Promise<ISessionJobsResponse> {
    let result: ISessionJobsResponse;
    try {
        const res = await axios.get("/api/recent-review");
        result = {
            success: true,
            data: res.data,
            msg: ""
        }
    } catch (error) {
        console.error("Error fetching session jobs:", error);
        result = {
            success: false,
            data: null,
            msg: "Error fetching session jobs"
        };
    }
    return result;
}

export async function getRateLimitInfo(): Promise<IRateLimitInfoResponse> {
    let result: IRateLimitInfoResponse = {
        success: false,
        data: null,
        msg: ""
    };
    try {
        const res = await axios.get("/api/generate-review");
        if (res.headers["x-ratelimit-remaining-user"]) {
            result = {
                success: true,
                data: {
                    remainingUserSubmissions: parseInt(
                        res.headers["x-ratelimit-remaining-user"]
                    ),
                    remainingTotalSubmissions: parseInt(
                        res.headers["x-ratelimit-remaining-total"]
                    ),
                    nextResetTime: res.headers["x-ratelimit-reset"],
                },
                msg: ""
            }
        }
    } catch (error) {
        console.error("Error fetching rate limit info:", error);
        result = {
            success: false,
            data: null,
            msg: "Error fetching rate limit info"
        };
    }
    return result;
}

export async function submitReview(inputFile: Blob, reviewType: TReviewType): Promise<ISubmitReviewResponse> {
    let result: ISubmitReviewResponse = {
        success: false,
        data: null,
        msg: ""
    };
    try {
        const headers = {
            "Content-Type": "multipart/form-data",
        };
        const formData = new FormData();
        formData.append("pdf_file", inputFile);
        formData.append("review_type", reviewType);

        const res = await axios.post("/api/generate-review", formData, {
            headers: headers,
        });

        if (res.headers["x-ratelimit-remaining-user"]) {
            result = {
                success: true,
                data: {
                    job: res.data,
                    rate_limit_info: {
                        remainingUserSubmissions: parseInt(
                            res.headers["x-ratelimit-remaining-user"]
                        ),
                        remainingTotalSubmissions: parseInt(
                            res.headers["x-ratelimit-remaining-total"]
                        ),
                        nextResetTime: res.headers["x-ratelimit-reset"],
                    }
                },
                msg: ""
            }
        }
    } catch (error) {
        console.error("Error fetching rate limit info:", error);
        let msg = "";
        if (axios.isAxiosError(error) && error.response?.status === 429) {
            msg = error.response.data.message ||
                "You've reached the maximum number of submissions for today. Please try again tomorrow.";
        }
        else {
            msg = "Error submitting form.";
        }
        result = {
            success: false,
            data: null,
            msg: msg
        };
    }
    return result;
}