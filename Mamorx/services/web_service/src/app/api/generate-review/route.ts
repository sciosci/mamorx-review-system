import { NextResponse } from 'next/server'
// import { loadEnvConfig } from '@next/env';

// const projectDir = process.cwd();
// loadEnvConfig(projectDir);
export const dynamic = "force-dynamic";

export async function GET() { // request: NextRequest
    const mamorx_service_url = process.env.MAMORX_SERVICE_URL;
    console.log(`backend url : ${mamorx_service_url}`);
    return NextResponse.json({ msg: `Hello from server: ${mamorx_service_url}` });
}