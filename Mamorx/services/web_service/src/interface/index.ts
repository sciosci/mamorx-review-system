export interface ReviewResult {
    review_content: string,
    time_elapsed: number,
    novelty_assessment: string,
    figure_critic_assessment: string
};

export interface PaperReviews {
    paper_id: string,
    authors: string,
    title: string,
    pdf_url: string,
    barebones: ReviewResult,
    liangetal: ReviewResult,
    multiagent: ReviewResult,
    mamorx: ReviewResult
};