from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# <<Implement your APIs here>>
@app.post("/generatecode/")
async def generate_code(input_text: str = Form(...)):
    # Process the input_text here (for demonstration, we just echo it)
    op = f"""{input_text} is generated"""
    processed_text = f"Processed: {op} "
    print(processed_text)
    return JSONResponse(content={"result": processed_text})
