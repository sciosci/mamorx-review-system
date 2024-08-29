from PIL import Image
from papermage.recipes import CoreRecipe
import boto3
from botocore.exceptions import ClientError
from typing import TypedDict, List
from anthropic import AnthropicBedrock
from crewai_tools import BaseTool
import json

class ExtractedFigureCaption(TypedDict):
    figures: List[Image.Image]
    captions: List[str]

class FigureAgent(BaseTool):
    name:str = "figure-agent"
    description:str = ""

    def extract_figures_and_captions(self, pdf_file_path: str) -> ExtractedFigureCaption:
        doc = self.recipe.run(pdf_file_path)

        image_list = list()
        # Parse Images
        for i, fig in enumerate(doc.figures):
            figure_box = fig.boxes[0]

            # Get page image
            page_image = doc.images[figure_box.page]
            page_w, page_h = page_image.pilimage.size

            figure_box_xy = figure_box.to_absolute(page_width=page_w, page_height=page_h).xy_coordinates

            extracted_image: Image.Image = page_image._pilimage.crop(figure_box_xy)

            image_list.append(extracted_image)
            # Save image to target directory
            # extracted_image.save(f"{output_file_directory}/img_{i}.png", format="PNG")

        # Parse Captions
        caption_list = list(map(lambda caption: caption.text, doc.captions))

        return ExtractedFigureCaption(figures=image_list, captions=caption_list)
    
    def assess_figures_and_captions(self, client, argument, figure_caption_dict):
        pass
    
    # Placeholder from AWS guide
    def send_prompt():
        MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
        IMAGE_NAME = "primary-energy-hydro.png"
        bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

        with open(IMAGE_NAME, "rb") as f:
            image = f.read()

        user_message = "Which countries consume more than 1000 TWh from hydropower? Think step by step and look at all regions. Output in JSON."

        messages = [
            {
                "role": "user",
                "content": [
                    {"image": {"format": "png", "source": {"bytes": image}}},
                    {"text": user_message},
                ],
            }
        ]

        response = bedrock_runtime.converse(
            modelId=MODEL_ID,
            messages=messages,
        )

        response_text = response["output"]["message"]["content"][0]["text"]
        return response_text

    def __init__(self):
        self.recipe = CoreRecipe()
        

