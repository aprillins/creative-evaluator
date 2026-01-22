import os
from typing import Dict, Literal, Optional
from dotenv import load_dotenv
import gradio as gr
from langchain.agents import create_agent
import langchain_core
from langsmith import Client
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import base64
from io import BytesIO
from PIL import Image
from pydantic import BaseModel, Field
import json

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
brand_name = os.getenv("BRAND_NAME")  
brand_description = os.getenv("BRAND_DESCRIPTION") 

llm = ChatOpenAI(model="gpt-4.1")

class ImageReadingResult(BaseModel):    
    # Categoricals
    type_of_promotion: Literal["Acquisition", "Retention", "Others", "Unclear"] = Field(..., description="Type of promotion depicted in the image. Do not assume, if it's unclear it's unclear")
    promo_font_size_readability: Literal["Small", "Medium", "Large", "Unclear"] = Field(..., description="Assessment of promo font size readability compared to the overall image.")
    promo_value: Optional[Dict[str, int]] = Field(None, description="What is the promo value offered?")
    promo_term: Literal[
        "Trade for the first time",
        "Invite friends",
        "Existing users should trade",
        "Both first time trading users and existing users should trade to get the reward",
        "Unclear"
    ] = Field(..., description="What should the user do to get the promo?")
    creative_size: Optional[Dict[str, int]] = Field(..., description="size in pixel width and height")

    # Scoring (add more keys if you want per-feature granularity)
    overall_score: int = Field(..., ge=0, le=10, description="Overall score for image content clarity and promotional communication.")
    aspect_scores: Optional[Dict[str, int]] = Field(
        None, 
        description="Optional detailed scores per aspect (0-10), for example: {'brand_name_clarity': 8, 'promo_value_highlight': 9, ...}"
    )

    # Optional: Comments or Recommendations
    recommendation: Optional[str] = Field(None, description="Recommendations for improvement or observation notes.")

    class Config:
        json_schema_extra = {
            "example": {
                "description": "The image shows the brand logo at the top left, a bold headline 'Welcome Bonus Rp50.000', underneath is the tagline 'Trade crypto for the first time'. The promo code is highlighted with a large and clear font. The background is blue with ample whitespace, making the text readable.",
                "type_of_promotion": "Acquisition",
                "promo_font_size_readability": "Large",
                "promo_value": "Rp50.000",
                "creative_size": {"w": 1280, "h": 500},
                "promo_term": "Trade for the first time",
                "overall_score": 9,
                "aspect_scores": {
                    "brand_name_clarity": 9,
                    "promo_value_highlight": 10,
                    "how_to_get_promo_clarity": 8,
                    "visual_balance": 9
                },
                "recommendation": "Ensure the promo period is visible and add a brief how-to section for claiming the reward."
            }
        }

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
<<<<<<< HEAD
            You are a ad creative evaluator. You give a detailed assessment of ad creative readability and understandability for the {brand_name} brand.
            Imagine you are a user seeing an image provided for the first time.
            YOU ANSWER WITH "brand is not {brand_name}" if the creative is not a promotional creative created by {brand_name} brand.
=======
                You are a promotional image analyst. You act as a person who sees a promotional image for the first time. 
                Your purpose is to analyze and give the reasons whether a promotional image is understandable or not.
>>>>>>> 72e5099 (improve model)
            """)
        messages: list[SystemMessage | HumanMessage] = [message]

        message = HumanMessage(
            content = [
                {"type": "text", "text": f"""
<<<<<<< HEAD
                What is in this image? Describe it in detail. Additionally, it has the following properties:\n{img_info}
                First you have to determine if the creative is a promotional creative created by a {brand_name} brand or not. {brand_description}.
                If you find that the creative is a promotional creative created by {brand_name} brand, then you have to answer the following questions about the promotional creative readability and understandability.
                If the creative is not a promotional creative from {brand_name} brand. Then you answer with "ABORTED OPERATION" only
                Also, you should ask yourself these questions:
                    1. Is the message clear?
                    2. Is the font size appropriate?
                    3. Are the text colors contrasting well with the background?
                    4. Is the safe zone already applied?
                    5. Do you understand the meaning of the image?
                    6. Does the creative show any promotional messages?
                    7. If you the creative show promotional message, then what type of promotion is this? Is it acquisition, Retention, Others, or Unclear?
=======
                    Based on the provided image give your analysis and scoring (0-10) regarding the following items:
                    - Is the content and context in the image understandable?
                    - Brand name clarity
                    - Image size
                    - Image resolution
                    - Image width and height in pixel
                    - Title/Headline size
                    - Title/Headline clarity
                    - Type of promotion (user retention, new user acquisition, referral, others, or unclear). If you think it's a bit unclear, then it's unclear
                    - Value of the promotion
                    - Benefit
                    - How to get the promo
                    - Promo period (if there's none put none not score)
                    - Ratio between text and empty space to make sure it's not too empty or crowded
                    - Based on the image size and text in it, can it be clearly read on mobile?
                    - Based on the image size and text in it, is it suitable for digital ads like Meta Ads, TikTok Ads?
                    - Based on the image size and text in it, is it suitable for one of the Google Play or App Store app screenshots?
                    - Is it understandable for people who see it for the first time and never interact with the brand
                    Give suggestions to improve the promotional image if any.
                    Additional image info: \n{img_info}
>>>>>>> 72e5099 (improve model)
                """},
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
    outputs=gr.Markdown(label="Evaluation Result", min_height=150),
    title="Creative Evaluator",
    description="Upload an image to evaluate its creativity."
)

if __name__ == "__main__":
    demo.launch()