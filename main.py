import os
from typing import Dict, Literal
from dotenv import load_dotenv
import gradio as gr
from langchain.agents import create_agent
import langchain_core
import langchain_community
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import base64
from io import BytesIO
from PIL import Image
from pydantic import BaseModel, Field
import json

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4.1")


class ImageReadingResult(BaseModel):
    description: str = Field(..., description="Detailed description of the image content.")
    type_of_promotion: Literal["Acquisition", "Retention", "Others", "Unclear"] = Field(..., description="Type of promotion depicted in the image.")
    promo_font_size_readability: Literal["Small", "Medium", "Large", "Unclear"] = Field(..., description="Assessment of promo font size readability compared to the whole image.")
    promo_value: str = Field(..., description="What is the amount of promo that pintu offer?")
    promo_term: Literal["Trade for the first time", "Invite friends", "Existing users should trade", "Both first time trading users and existing users should trade to get the reward", "Unclear"] = Field(..., description="What should user do to get the promo?")


def get_basic_image_info(img: Image.Image):
    img_context = (
        f"- Size: {img.size[0]}x{img.size[1]} pixels\n"
        f"- Width: {img.width} pixels\n"
        f"- Height: {img.height} pixels\n"
        f"- Format: {img.format}\n"
        f"- Mode: {img.mode}"
    )
    print(img_context)
    return img_context



def pil_image_to_base64(img: Image.Image, format="jpeg") -> Dict[str, str]:
    buffered = BytesIO()
    img.save(buffered, format=format)
    exif = img.getexif()
    for key, value in exif.items():
        print(f"EXIF {key}: {value}") 
    image_info = get_basic_image_info(img)

    return {"base64": base64.b64encode(buffered.getvalue()).decode(), "info": image_info}

def evaluate_creativity(image: Image.Image) -> str:
    # Placeholder for creativity evaluation logic
    # You can integrate OpenAI API here to analyze the image

    if image is not None:
        img = pil_image_to_base64(image)
        img_b64 = img['base64']
        img_info = img['info']  
        message = SystemMessage(
            content = """
            You are a ad creative evaluator. You give a detailed assessment of ad creative readability.
            Imagine you are a user seeing this image for the first time. You should ask yourself these questions:
            1. Is the message clear?
            2. Is the font size appropriate?
            3. Are the text colors contrasting well with the background?
            4. Is the safe zone already applied?
            5. Do you understand the meaning of the image?
            6. What type of promotion is this? (Acquisition, Retention, Others, Unclear)
            """)
        messages = [message]

        message = HumanMessage(
            content = [
                {"type": "text", "text": f"What is in this image? Describe it in detail. Additionally, it has the following properties:\n{img_info}"},
                {"type": "image", "base64": img_b64, "mime_type": "image/jpeg"}
            ]
        )
        messages.append(message)


        ## alternative method to use url
        # img_data_uri = f"data:image/jpeg;base64,{img_b64}"
        # message = HumanMessage(
        #     content = [
        #         {"type": "text", "text": "What is in this image? Describe it in detail."},
        #         {"type": "image_url", "image_url": {"url": f"{img_data_uri}"}},
        #     ]
        # )

        try:
            # response = llm.invoke(messages)
            llm_with_structured_response = llm.with_structured_output(ImageReadingResult)
            structured_response = llm_with_structured_response.invoke(messages)
        except Exception as e:
            print(f"Error invoking LLM: {e}")
            return f"Error processing image: {e}"        
        return "```json\n" + structured_response.model_dump_json(indent=2) + "\n```"
    
    else:
        return "No image uploaded."

demo = gr.Interface(
    fn=evaluate_creativity,
    inputs=gr.Image(type="pil", label="Upload an Image"),
    outputs=gr.Markdown(label="Evaluation Result", ),
    title="Creative Evaluator",
    description="Upload an image to evaluate its creativity."
)

if __name__ == "__main__":
    demo.launch()