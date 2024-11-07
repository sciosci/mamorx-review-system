"use client"
import React from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Label
} from "@/components/ui/label"
import {
  Input
} from "@/components/ui/input"


const FormSchema = z.object({
  review_type: z
    .string({
      required_error: "Please select a review source.",
    }),
})


export default function PDFReviewerForm() {
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  })
  const [pdfData, setPDFData] = React.useState<string>("");
  const [inputFile, setInputFile] = React.useState<File>();

  function handlePDFChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target?.files?.[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onloadend = () => {
        setPDFData(reader.result as string);
      };
      reader.readAsDataURL(file);
      setInputFile(file);
    }
  }

  function onSubmit(data: z.infer<typeof FormSchema>) {
    console.log(JSON.stringify(data));
    console.log(pdfData);
    console.log(inputFile);
    // toast({
    //   title: "You submitted the following values:",
    //   description: (
    //     <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
    //       <code className="text-white">{JSON.stringify(data, null, 2)}</code>
    //     </pre>
    //   ),
    // })
  }


  return (
    <div>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="w-2/3 space-y-6">
          <FormField
            control={form.control}
            name="review_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Review Type</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a type of review" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="barebones">barebones</SelectItem>
                    <SelectItem value="liangetal">liangetal</SelectItem>
                    <SelectItem value="multiagent">multiagent</SelectItem>
                    <SelectItem value="mamorx">mamorx</SelectItem>
                  </SelectContent>
                </Select>
                <FormDescription>
                  You can select a type of review for your scientific article
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="grid w-full max-w-sm items-center gap-1.5">
            <Label htmlFor="file">PDF file</Label>
            <Input id="pdf_file" type="file" accept=".pdf" onChange={handlePDFChange}/>
          </div>
          <Button type="submit">Submit</Button>
        </form>
      </Form>
    </div>
  );
};



