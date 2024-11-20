import { NextResponse, NextRequest } from "next/server";
import axios from "axios";
import fs from "fs";
import path from "path";
import { promisify } from "util";
import {
  getRateLimitInfo,
  incrementSubmissionCount,
  getGlobalSubmissionCount,
} from "@/lib/db";

const unlinkAsync = promisify(fs.unlink);
const writeFileAsync = promisify(fs.writeFile);

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const sessionId = request.headers.get("x-session-id");
  if (!sessionId) {
    return NextResponse.json({ message: "Invalid session" }, { status: 401 });
  }

  try {
    const userLimit = await getRateLimitInfo(sessionId);
    const globalCount = await getGlobalSubmissionCount();

    return NextResponse.json(
      { msg: "Rate limit info retrieved successfully" },
      {
        headers: {
          "X-RateLimit-Remaining-User": (
            3 - userLimit.submissions_count
          ).toString(),
          "X-RateLimit-Remaining-Total": (500 - globalCount).toString(),
          "X-RateLimit-Reset": new Date(userLimit.last_reset).toISOString(),
        },
      }
    );
  } catch (error) {
    console.error("Error getting rate limit info:", error);
    return NextResponse.json(
      { message: "Error retrieving rate limit info" },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  const sessionId = request.headers.get("x-session-id");
  if (!sessionId) {
    return NextResponse.json({ message: "Invalid session" }, { status: 401 });
  }

  try {
    const userLimit = await getRateLimitInfo(sessionId);
    const globalCount = await getGlobalSubmissionCount();

    if (userLimit.submissions_count >= 3) {
      return NextResponse.json(
        {
          message: "Daily submission limit reached. Please try again tomorrow.",
        },
        {
          status: 429,
          headers: {
            "X-RateLimit-Remaining-User": "0",
            "X-RateLimit-Remaining-Total": (500 - globalCount).toString(),
            "X-RateLimit-Reset": new Date(userLimit.last_reset).toISOString(),
          },
        }
      );
    }

    if (globalCount >= 500) {
      return NextResponse.json(
        {
          message: "Global submission limit reached. Please try again later.",
        },
        {
          status: 429,
          headers: {
            "X-RateLimit-Remaining-User": (
              3 - userLimit.submissions_count
            ).toString(),
            "X-RateLimit-Remaining-Total": "0",
            "X-RateLimit-Reset": new Date(userLimit.last_reset).toISOString(),
          },
        }
      );
    }

    await incrementSubmissionCount(sessionId);

    const mamorx_service_url =
      process.env.MAMORX_SERVICE_URL || "http://mamorx-service";
    const formData = await request.formData();
    const review_type = formData.get("review_type") as string;

    const pdf_file = formData.get("pdf_file") as File;
    const tempFilePath = path.join(
      "/tmp",
      `temp_${Date.now()}_${pdf_file.name}`
    ); // Temporary file path with a random name

    // Read the file from the FormData and save it to a temporary location
    const arrayBuffer = await pdf_file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    await writeFileAsync(tempFilePath, buffer);

    // Log the contents of the request form
    console.log("Review Type:", review_type);
    console.log("Temporary File Path:", tempFilePath);

    const request_form = new FormData();
    // Read the file into a Buffer and create a Blob
    const fileBuffer = fs.readFileSync(tempFilePath);
    const blob = new Blob([fileBuffer], { type: "application/pdf" }); // Create a Blob from the buffer

    // Append the Blob to the FormData
    request_form.append("pdf_file", blob, pdf_file.name); // Use the temporary file
    // Log the FormData contents for debugging
    Array.from(request_form.entries()).forEach(([key, value]) => {
      console.log(`${key}:`, value);
    });

    const server_response = await axios.post(
      `${mamorx_service_url}/review/submit-pdf-to-queue?review_type=${encodeURIComponent(
        review_type
      )}`,
      request_form,
      {
        headers: {
          "Content-Type": "multipart/form-data",
          "session-id": sessionId
        },
      }
    );

    // Clean up the temporary file
    await unlinkAsync(tempFilePath);

    return NextResponse.json(server_response.data, {
      headers: {
        "X-RateLimit-Remaining-User": (
          2 - userLimit.submissions_count
        ).toString(),
        "X-RateLimit-Remaining-Total": (499 - globalCount).toString(),
        "X-RateLimit-Reset": new Date(userLimit.last_reset).toISOString(),
      },
    });
  } catch (error) {
    console.error("Error processing request:", error);
    return NextResponse.json(
      { message: "Internal server error" },
      { status: 500 }
    );
  }
}
