import { NextResponse, NextRequest } from "next/server";
import axios from "axios";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const sessionId = request.headers.get("x-session-id");
  if (!sessionId) {
    return NextResponse.json({ message: "Invalid session" }, { status: 401 });
  }

  try {
    const mamorx_service_url =
      process.env.MAMORX_SERVICE_URL || "http://mamorx-service";

    const server_response = await axios.get(`${mamorx_service_url}/review/review-jobs`,
      {
        headers: {
          "session-id": sessionId
        }
      }
    );

    return NextResponse.json(server_response.data);
  } catch (error) {
    console.error("Error processing request:", error);
    return NextResponse.json(
      { message: "Internal server error" },
      { status: 500 }
    );
  }


}
