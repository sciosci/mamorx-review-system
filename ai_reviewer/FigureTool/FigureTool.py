from PIL import Image
from papermage.recipes import CoreRecipe
from typing import TypedDict, List
from anthropic import AnthropicBedrock
from crewai_tools import BaseTool
import io
import base64

MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

class PaperArgument(TypedDict):
    title: str
    abstract: str

class ExtractedFigureCaption(TypedDict):
    figures: List[Image.Image]
    captions: List[str]

class FigureTool(BaseTool):
    name:str = "figure-tool"
    description:str = ""
    

    def _run(self, argument: dict) -> list[str]:
        pass

    def extract_figures_and_captions(self, pdf_file_path: str) -> ExtractedFigureCaption:
        recipe = CoreRecipe()
        doc = recipe.run(pdf_file_path)

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

        # Parse Captions
        caption_list = list(map(lambda caption: caption.text, doc.captions))

        return ExtractedFigureCaption(figures=image_list, captions=caption_list)
    
    def image_to_png_bytes(self, image: Image.Image) -> bytes:
        io_buffer = io.BytesIO()
        # Save image as png
        image.save(io_buffer, format="PNG")

        return io_buffer.getvalue()

    def assess_figures_and_captions(self, client: AnthropicBedrock, argument:PaperArgument, figure_caption_dict: ExtractedFigureCaption):
        # Assess Clarity for each image
        clarity_assesment:List[str] = list()

        # Get summary for each image
        summary_list:str = list()

        for image in figure_caption_dict["figures"]:
            image_in_bytes = self.image_to_png_bytes(image)
            image_data = base64.b64encode(image_in_bytes).decode("utf-8")
            # Assess Clarity
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source":  {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": f'''
                        Given the abstract of an academic paper and captions below, generate a short review on the clarity and consistency between the given image with the provided captions and the abstract. Be as critical and skeptical as possible. It is crucial that inconsistencies are pointed out to avoid misinformation. If there are any inconsistencies, please list them out as well.
                         
                         Abstract: {argument["abstract"]},

                         Captions: {figure_caption_dict["captions"]}
                        '''},
                    ],
                }
            ]

            response = self.__send_prompt(
                client=client,
                model_id=MODEL_ID,
                messages=messages,
                max_tokens=512
            )

            clarity_assesment.append(response.strip())

            # Get summary description of image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source":  {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": f'''Generate a short description of the provided image. Also describe the implications conveyed within the image'''
                        },
                    ],
                }
            ]

            response = self.__send_prompt(
                client=client,
                model_id=MODEL_ID,
                messages=messages,
                max_tokens=1024
            )

            clarity_assesment.append(response.strip())

            summary_list.append(response.strip())

        all_clarity = "\n".join(clarity_assesment)
        all_summary = "\n----------------------------------------------".join(summary_list)
        # Concatnate the results
        final_result:str = f'''
        ##################################################
        CLARITY ASSESSMENT
        {all_clarity}
        ##################################################
        ##################################################
        SUMMARY OF EACH FIGURE
        {all_summary}
        ##################################################
        '''

        return final_result
    
    def __send_prompt(self, client: AnthropicBedrock, model_id: str, messages, max_tokens: int) -> str:
        response = client.messages.create(
                model=MODEL_ID,
                max_tokens=max_tokens,
                messages=messages
            )
        
        content = response.content
        if isinstance(content, list) and len(content) > 0:
            content = content[0].text
        else:
            content = str(content)

        content = content.strip()

        return content


