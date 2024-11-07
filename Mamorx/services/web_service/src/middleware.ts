import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { v4 as uuidv4 } from "uuid";

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Check for existing session
  let sessionId = request.cookies.get("session_id")?.value;

  // Create new session if none exists
  if (!sessionId) {
    sessionId = uuidv4();
    // Set session cookie that expires in 24 hours
    response.cookies.set({
      name: "session_id",
      value: sessionId,
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 60 * 60 * 24, // 24 hours
    });
  }

  // Add session to request headers for use in API routes
  response.headers.set("x-session-id", sessionId);

  return response;
}

export const config = {
  matcher: "/api/:path*",
};
