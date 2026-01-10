from fastapi import FastAPI
import gradio as gr
from main import demo
app = FastAPI()

@app.get("/")
async def root():
    return "running creative-evaluator app"

app = gr.mount_gradio_app(app, demo, path="/main")