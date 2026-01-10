import os
from typing import Dict
from dotenv import load_dotenv
import gradio as gr
import langchain_core
import langchain_community
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import base64
from io import BytesIO
from PIL import Image

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4.1-mini")

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
        message = HumanMessage(
            content = [
                {"type": "text", "text": f"What is in this image? Describe it in detail. Additionally, it has the following properties:\n{img_info}"},
                {"type": "image", "base64": img_b64, "mime_type": "image/jpeg"}
            ]
        )

        ## alternative method to use url
        # img_data_uri = f"data:image/jpeg;base64,{img_b64}"
        # message = HumanMessage(
        #     content = [
        #         {"type": "text", "text": "What is in this image? Describe it in detail."},
        #         {"type": "image_url", "image_url": {"url": f"{img_data_uri}"}},
        #     ]
        # )

        try:
            response = llm.invoke([message])
        except Exception as e:
            print(f"Error invoking LLM: {e}")
            return f"Error processing image: {e}"

        return response.content
    else:
        return "No image uploaded."

demo = gr.Interface(
    fn=evaluate_creativity,
    inputs=gr.Image(type="pil", label="Upload an Image"),
    outputs=gr.Textbox(label="Evaluation Result", lines=10),
    title="Creative Evaluator",
    description="Upload an image to evaluate its creativity."
)

if __name__ == "__main__":
    demo.launch()