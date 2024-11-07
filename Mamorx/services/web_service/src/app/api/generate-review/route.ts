import { NextResponse, NextRequest } from "next/server";
import axios from "axios";
import fs from "fs";
import path from "path";
import { promisify } from "util";

const unlinkAsync = promisify(fs.unlink);
const writeFileAsync = promisify(fs.writeFile);

export const dynamic = "force-dynamic";

export async function GET() {
  const mamorx_service_url = process.env.MAMORX_SERVICE_URL;
  console.log(`backend url : ${mamorx_service_url}`);
  return NextResponse.json({ msg: `Hello from server: ${mamorx_service_url}` });
}

export async function POST(request: NextRequest) {
  const mamorx_service_url =
    process.env.MAMORX_SERVICE_URL || "http://mamorx-service";
  const formData = await request.formData();
  const review_type = formData.get("review_type") as string;

  const pdf_file = formData.get("pdf_file") as File;
  const tempFilePath = path.join("/tmp", `temp_${Date.now()}_${pdf_file.name}`); // Temporary file path with a random name

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

  try {
    const server_response = await axios.post(
      `${mamorx_service_url}/review/review-pdf-paper?review_type=${encodeURIComponent(
        review_type
      )}`,
      request_form,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    // Clean up the temporary file
    await unlinkAsync(tempFilePath);

    return NextResponse.json(server_response.data);
  } catch (error) {
    console.error(
      "Error with connecting to server:",
      error instanceof Error ? error.message : error
    );
    // Clean up the temporary file in case of error
    await unlinkAsync(tempFilePath);
    return NextResponse.json(
      { msg: "Error with connecting to server" },
      { status: 500 }
    );
  }
}
