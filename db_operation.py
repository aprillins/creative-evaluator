from langchain_community.vectorstores import Chroma
from chromadb import CloudClient
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import base64
from io import BytesIO
from PIL import Image
import os

openai_api_key = os.getenv("OPENAI_API_KEY")
chromadb_api_key = os.getenv("CHROMA_API_KEY")
chromadb_host = os.getenv("CHROMA_HOST")
chromadb_tenant = os.getenv("CHROMA_TENANT")
chromadb_database = os.getenv("CHROMA_DATABASE")

embeddings = OpenAIEmbeddings()

def connect_to_chroma_cloud():
    """
    Docstring for connect_to_chroma_cloud
    Connect to chroma cloud and return chroma instance
    """
    cloud_client = CloudClient(
        tenant=chromadb_tenant,
        database=chromadb_database,
        api_key=chromadb_api_key
    )
    return cloud_client

def create_new_database():
    """
    Create a new chroma database
    This is a vector database for storing image 
    There should be these metadata: type (value: original or existing), pillar (value: retail, pro spot, futures, others), month (format: mm), year (format: yyyy)
    """
    vector_store = Chroma(
        client=connect_to_chroma_cloud(),
        embedding_function=embeddings,
        collection_name=collection_name
    )
    return vector_store

def get_image_basedon_query(query: str):
    """
    Docstring for get_image_basedon_query
    Perform similarity search based on query
    :param query: Description
    :type query: str
    """
    results = vector_store.similarity_search(query)
    return results

def store_new_image(image_path: str, type_val: str, pillar: str, month: str, year: str):
    """
    Store a new image in the database
    """
    image = Image.open(image_path)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    image_url = f"data:image/jpeg;base64,{img_str}"
    llm = ChatOpenAI(model="gpt-4-vision-preview")
    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": "Describe this image in detail."},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}
    ]
    response = llm.invoke(messages)
    description = str(response.content)
    metadata = {
        "type": type_val,
        "pillar": pillar,
        "month": month,
        "year": year
    }
    vector_store.add_texts([description], metadatas=[metadata])
    return "Image stored successfully"

def evaluate_image(image):
    """
    Evaluate the creativity of the image
    """
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    image_url = f"data:image/jpeg;base64,{img_str}"
    llm = ChatOpenAI(model="gpt-4-vision-preview")
    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": "Evaluate the creativity of this image on a scale of 1 to 10, where 1 is not creative and 10 is highly creative. Provide a brief explanation."},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]}
    ]
    response = llm.invoke(messages)
    return response.content

vector_store = create_new_database()