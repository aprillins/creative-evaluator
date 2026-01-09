import os
from dotenv import load_dotenv
import gradio as gr
import langchain_core
import langchain_community
import langchain_openai
import db_operation as dbo

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print(f"OPENAI_API_KEY: {api_key}")

def evaluate_creativity(image):
    # Placeholder for creativity evaluation logic
    # You can integrate OpenAI API here to analyze the image
    if image is not None:
        return "Image uploaded successfully! Creativity evaluation coming soon."
    else:
        return "No image uploaded."

demo = gr.Interface(
    fn=evaluate_creativity,
    inputs=gr.Image(type="pil", label="Upload an Image"),
    outputs=gr.Textbox(label="Evaluation Result"),
    title="Creative Evaluator",
    description="Upload an image to evaluate its creativity."
)

if __name__ == "__main__":
    demo.launch()