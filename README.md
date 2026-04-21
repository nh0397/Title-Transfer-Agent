# Title Transfer Agent

The Title Transfer Agent is an automated system designed to streamline the processing and transfer of manufactured home titles within California. It utilizes multimodal artificial intelligence to extract data from official scanned documents and programmatically populates the corresponding government forms required by the California Department of Housing and Community Development (HCD).

## Core Capabilities

The system operates through a structured four-phase pipeline:

1.  **Data Extraction**: Uses vision-capable large language models (LLMs) to scan high-resolution images of California Certificates of Title. It identifies and extracts key data points such as Manufacturer details, Serial Numbers, Decal Numbers, and Registered Owner information.
2.  **Schema Mapping**: Automatically maps extracted raw data to the specific field IDs required by various HCD forms. This phase ensures data consistency across multiple documents and formats addresses into government-compliant structures.
3.  **PDF Generation**: Programmatically fills official HCD PDF templates (476.6G, 480.5, and 476.6) using the mapped data while preserving the original document structure and layout.
4.  **Verification and Review**: Provides a web-based interface for users to preview the generated PDFs side-by-side with an editable data panel. This allows for manual corrections and instant re-generation of documents before final download.

## Technology Stack & Design Decisions

- **Backend (Python & FastAPI)**: Chosen for its native asynchronous capabilities, rich data science/AI ecosystem, and native support for fast I/O document processing. Python provides the best-in-class libraries (`pypdf` / `PyMuPDF`) for manipulating complex PDF AcroForms.
- **Frontend (React)**: Selected for its component-based architecture, which makes building complex dynamic dashboards (like our side-by-side PDF preview and inline edit panel) straightforward.
- **AI Engine (Local/Cloud Hybrid via Groq/Ollama)**: We utilize Llama Vision models (e.g., Llama 4 Scout/Llama 3.2 Vision) for extraction and text models for schema mapping. Groq was selected on the cloud side for its near-zero latency inference, which is critical for synchronous web requests. We included a fallback local pipeline (Ollama) to ensure the system can prioritize data privacy for sensitive PII when latency is less critical.
- **PDF Infrastructure**: `PyMuPDF` is used for high-fidelity rendering of PDFs to images (vital for vision LLM accuracy), while `pypdf` is used to append AcroForm fields.

### Scaling Limitation: The Size Approach

Attempting to improve this system's accuracy or capability *solely* by scaling up the AI model size (e.g., swapping a 11B parameter model for a 405B parameter model) presents a critical limiting factor: **Latency vs. Context Efficiency**. 
Large vision models are computationally expensive and slow to process high-resolution images. In a production environment handling thousands of transfers, pushing a massive model against a strict synchronous web request will lead to severe UI blocking, queue timeouts, and exorbitant compute costs per title. Furthermore, larger models often suffer from "context destruction" when reading dense, highly structured government tables, where a smaller, specifically fine-tuned OCR-focused vision model coupled with a deterministic rules-engine would scale much more efficiently and reliably.

## Installation and Setup

### Backend Configuration

1. Navigate to the backend directory.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure the `.env` file with your Groq API Key and desired model names.
4. Start the server: `python main.py`.

### Frontend Configuration

1. Navigate to the frontend directory.
2. Install dependencies: `npm install`.
3. Start the development server: `npm run dev`.

## Project Structure

- **backend/main.py**: Entry point for the FastAPI application.
- **backend/routes/**: Contains the API endpoints for processing and file management.
- **backend/services/**: Core business logic for LLM orchestration and PDF manipulation.
- **backend/prompts.py**: Stores the complex instruction sets for the AI agent.
- **templates/**: Official HCD PDF templates used for generation.
