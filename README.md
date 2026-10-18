# AI-Powered Invoice & Receipt Automation

An invoice and receipt processing application built with **Python, FastAPI, PaddleOCR, Ollama, and PostgreSQL**. The application extracts text from uploaded documents, uses a locally running large language model (LLM) to interpret the extracted text, and converts unstructured document content into structured data for validation and storage. 

Purpose of this app is to speed up manual invoice and receipt data entry works.

## Features

- **OCR Text Extraction:** Uses PaddleOCR to extract text from invoice and receipt images.
- **LLM-Powered Data Extraction:** Uses Ollama to interpret OCR output and identify relevant invoice fields.
- **Structured Data Output:** Converts extracted information into structured JSON.
- **Data Validation:** Uses Pydantic to validate extracted fields and data types.
- **Database Storage:** Uses PostgreSQL to persist document records and extracted data.
- **REST API:** Uses FastAPI to expose document-processing functionality.
- **Local LLM Inference:** Runs the language model locally through Ollama, avoiding the need for a third-party LLM API.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| FastAPI | REST API |
| PaddleOCR | Optical character recognition |
| Ollama | Local LLM inference and text interpretation |
| Qwen3 | Language model for field extraction |
| Pydantic | Data validation and structured output |
| PostgreSQL | Persistent data storage |
| Docker | Application containerisation |

## How It Works

1. **Document Input:** An invoice or receipt image is submitted for processing.
2. **Text Extraction:** PaddleOCR detects and recognizes text in the document.
3. **Data Interpretation:** Ollama interprets the OCR output and identifies relevant invoice fields.
4. **Structured Output:** The extracted information is converted into structured JSON.
5. **Validation:** Extracted values are validated before being accepted.
6. **Storage:** Document metadata and extracted information are stored in PostgreSQL.

## Extracted Fields

The application is designed to extract fields such as:

- Vendor name
- Invoice number
- Invoice date
- Currency
- Subtotal
- Tax amount
- Total amount

Field availability depends on the document content and extraction accuracy.

## Architecture

```text
Invoice / Receipt
       |
       v
   FastAPI API
       |
       v
    PaddleOCR
  (Text Extraction)
       |
       v
      Ollama
 (LLM Interpretation)
       |
       v
 Structured JSON
       |
       v
 Pydantic Validation
       |
       v
   PostgreSQL
```

## Getting Started

### Prerequisites

- Python 3.12
- Docker and Docker Compose
- Ollama
- A compatible Ollama model

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd invoice-automation
```

### 2. Configure Environment Variables

Create a `.env` file and configure the required application and database settings.

Do not commit `.env` files or credentials to version control.

### 3. Start the Services

If your project uses Docker Compose:

```bash
docker compose up --build
```

Ensure that PostgreSQL and Ollama are accessible from the application container and that the configured model has been downloaded.

### 4. Download the Ollama Model

For example, if the application is configured to use Qwen3 1.7B:

```bash
ollama pull qwen3:1.7b
```

The exact model and Ollama connection settings should match your application configuration.

### 5. Access the API

Once the API is running, open the FastAPI interactive documentation:

```text
http://localhost:8000/docs
```

## Design Considerations

- OCR and LLM interpretation are handled as separate stages to make debugging and improvements easier.
- Structured outputs help maintain consistent data formats.
- Extracted values should be validated because OCR errors and LLM misinterpretations can occur.
- Documents with missing or ambiguous fields should be flagged for manual review rather than treated as fully accurate.
- Local LLM inference reduces dependence on external LLM services, although hardware requirements and processing time depend on the model and workload.

## Future Improvements

- Support for PDF documents and multi-page invoices.
- Confidence scoring and automatic detection of uncertain fields.
- Human-in-the-loop review and correction.
- Improved validation of subtotal, tax, and total amounts.
- Background processing for large document volumes.
- Unit and integration testing.
- Deployment and monitoring for production workloads.

## Disclaimer

This project is intended for learning, experimentation, and demonstrating document-processing automation. Extraction results may require manual verification before being used for accounting or financial operations.

Example invoice and extracted fields.
<img width="489" height="457" alt="image" src="https://github.com/user-attachments/assets/d322082c-1761-4449-af36-9cd7fbe1f29a" />
<img width="1271" height="241" alt="image" src="https://github.com/user-attachments/assets/0a6e4e41-6df5-4bd7-8306-5943947c9e71" />



## License

Add a licence if you intend to distribute or reuse this project publicly.
