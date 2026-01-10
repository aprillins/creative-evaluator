import os
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

def pil_image_to_base64(img: Image.Image, format="PNG"):
    buffered = BytesIO()
    img.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode()

def evaluate_creativity(image: Image.Image):
    # Placeholder for creativity evaluation logic
    # You can integrate OpenAI API here to analyze the image
    
    print(f"type: {type(image)}")
    print(f"{image}")

    if image is not None:
        img_b64 = pil_image_to_base64(image)
        img_data_uri = f"data:image/png;base64,{img_b64}"
        message = HumanMessage(
            content = [
                {"type": "text", "text": "What is in this image? Describe it in detail."},
                {"type": "image_url", "image_url": {"url": f"{img_data_uri}"}},
            ]
        )
        response = llm.invoke([message])

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