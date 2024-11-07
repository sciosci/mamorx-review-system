import { NextResponse, NextRequest } from 'next/server'
import axios from 'axios';

export const dynamic = "force-dynamic";

export async function GET() { // request: NextRequest
    const mamorx_service_url = process.env.MAMORX_SERVICE_URL;
    console.log(`backend url : ${mamorx_service_url}`);
    return NextResponse.json({ msg: `Hello from server: ${mamorx_service_url}` });
}

export async function POST(request: NextRequest) {
    const mamorx_service_url = process.env.MAMORX_SERVICE_URL || "http://mamorx-service";
    const headers = {
        "Content-Type": "multipart/form-data"
    }
    const formData = await request.formData();
    const review_type = formData.get("review_type");

    formData.delete("review_type");

    console.log("Received formData");

    const pdf_file = formData.get("pdf_file") as File;
    const file_stream = pdf_file.stream();
    const stream_reader = file_stream.getReader();
    let file_contents = await stream_reader.read();
    let read_content = [];

    while(!file_contents.done)
    {
        read_content.push(file_contents.value);
        console.log(file_contents.value);
        file_contents = await stream_reader.read(); 
    }

    // console.log(read_content);

    let total_length = 0;
    read_content.forEach(item => {
        total_length += item.length;
    })

    let merged_array = new Uint8Array(total_length);
    let offset = 0;
    read_content.forEach(item => {
        merged_array.set(item, offset);
        offset += item.length;
    })

    console.log(merged_array);

    const request_form = new FormData();
    request_form.append("pdf_file", merged_array as Blob);


    // const formDataNew = new FormData();

    // formDataNew.append("pdf_file", "sample");

    // let server_response = undefined;
    // try {
    //     server_response = await axios.post(`${mamorx_service_url}/review/review-pdf-paper`, formDataNew, {
    //         params: {
    //             review_type: review_type
    //         },
    //         headers
    //     })
    //     console.log(server_response.status)
    // }
    // catch (err){
    //     console.log((err as any).status);
    //     console.log("Error with connecting to server");
    // }


    // console.log(server_response.data);
    console.log("Received Server Response");

    return NextResponse.json({ msg: `Hello from server: ${mamorx_service_url}` });
}