from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import pandas as pd
import matplotlib.pyplot as plt
import shutil

app = FastAPI()

def generate_report(file_path, output_path="cleaned_report.xlsx"):
    # Step 1: Read Excel file
    df = pd.read_excel(file_path)

    # Step 2: Clean data
    df = df.drop_duplicates()
    df = df.dropna()
    if "Customer" in df.columns:
        df["Customer"] = df["Customer"].astype(str).str.strip().str.upper()

    # Step 3: Group and summarize
    grouped = df.groupby("Customer")["Amount"].sum()

    # Step 4: Save charts
    grouped.plot(kind="bar", title="Total Amount by Customer (Cleaned)")
    plt.xlabel("Customer")
    plt.ylabel("Total Amount")
    plt.savefig("bar_chart.png")
    plt.close()

    grouped.plot(kind="pie", autopct="%1.1f%%", title="Customer Share")
    plt.ylabel("")
    plt.savefig("pie_chart.png")
    plt.close()

    # Step 5: Save cleaned data
    df.to_excel(output_path, index=False)

    return {
        "cleaned_file": output_path,
        "bar_chart": "bar_chart.png",
        "pie_chart": "pie_chart.png",
        "summary": grouped.to_dict()
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Save uploaded file locally
    with open(file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call report generator
    result = generate_report(file.filename)

    return {"message": "Report generated successfully", "result": result}

@app.get("/download/excel")
def download_excel():
    return FileResponse("cleaned_report.xlsx",
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        filename="cleaned_report.xlsx")

@app.get("/download/bar")
def download_bar_chart():
    return FileResponse("bar_chart.png", media_type="image/png", filename="bar_chart.png")

@app.get("/download/pie")
def download_pie_chart():
    return FileResponse("pie_chart.png", media_type="image/png", filename="pie_chart.png")
