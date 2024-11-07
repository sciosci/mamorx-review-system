import { NextResponse, NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
    console.log(request.nextUrl.searchParams);
    console.log(request.nextUrl.searchParams.get("query"));
    return NextResponse.json({ msg: 'Hello from server' })
}