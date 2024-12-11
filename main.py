from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
from app.extractors import table_extraction

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/extract/")
async def extract_table(
    request: Request,
    pdf_file: UploadFile = File(...),
    csv_file: UploadFile = File(...)
):
    # Save uploaded files
    pdf_path = os.path.join(UPLOAD_DIR, pdf_file.filename)
    csv_path = os.path.join(UPLOAD_DIR, csv_file.filename)
    with open(pdf_path, "wb") as buffer:
        buffer.write(pdf_file.file.read())
    with open(csv_path, "wb") as buffer:
        buffer.write(csv_file.file.read())

    # Read headers from CSV
    headers_df = pd.read_csv(csv_path,encoding="utf-8")
    headers = [header for header in headers_df[headers_df.columns[0]]]

    # Extract tables for each header
    extracted_data = []
    for header in headers:
        result_df = table_extraction(header, pdf_path)
        if result_df is not None:
            print(f"Data for header '{header}':")
            extracted_data.append(result_df) 
        else:
            print(f"Skipping header '{header}' because it was not found.")
    extracted_data = [df.reset_index(drop=True) for df in extracted_data]
    if extracted_data:
        extracted_data = pd.concat(extracted_data, axis=1)
        print("Concatenated DataFrame along columns:")
    else:
        print("No tables were found to concatenate.")


    output_csv_path = os.path.join(UPLOAD_DIR,"extracted_data.csv")
    extracted_data.to_csv(output_csv_path, index=False)


    return templates.TemplateResponse(
        "result.html",
        {"request": request, "download_url": f"/download/extracted_data.csv"}
    )


@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}
