# SETUP
- Create .env file
- Add the following variable inside the .env file
```
OPENAI_API_KEY="your openai api key"
CHROMA_API_KEY="your chromadb api key"
CHROMA_HOST="your host endpoint. If you are using chroma then put api.trychroma.com"
CHROMA_TENANT="your chroma tenant id"
CHROMA_DATABASE="your chroma database id"
```
Get your chroma credentials at trychroma.com in the database `Settings` tab

# DEPLOYING ON RENDER.COM

`uvicorn run:app --host 0.0.0.0 --port 5000`

### Set environment variable
Add `OPENAI_API_KEY` variable and fill the value
Add `PYTHON_VERSION` and fill `3.11.14` as the value
Don't forget to click save and deploy

# ACCESSING
After the page is published you can go to the page and access `/main`

