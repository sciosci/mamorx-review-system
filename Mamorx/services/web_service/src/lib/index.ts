export function formatDuration(ms: number): string {
    if (ms < 60000) {
        // less than a minute
        return `${ms / 1000} seconds`;
    } else {
        // minutes
        return `${ms / 60000} minutes`;
    }
}

export function formatTime(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}

export function getReviewDuration(reviewType: string): number {
    switch (reviewType) {
        case "barebones":
            return 10 * 1000; // 10 seconds
        case "liangetal":
            return 20 * 1000; // 20 seconds
        case "multiagent":
            return 20 * 60 * 1000; // 25 minutes
        case "mamorx":
            return 30 * 60 * 1000; // 30 minutes
        default:
            return 30 * 1000; // fallback
    }
}

export function isStringInArray(values: string[], key: string)
{
    for(const v of values)
    {
        if(v === key)
        {
            return true;
        }
    }
    return false;
}