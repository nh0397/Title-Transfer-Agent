# Title Transfer Agent

The Title Transfer Agent is an automated system designed to streamline the processing and transfer of manufactured home titles within California. It utilizes multimodal artificial intelligence to extract data from official scanned documents and programmatically populates the corresponding government forms required by the California Department of Housing and Community Development (HCD).

## Core Capabilities

The system operates through a structured four-phase pipeline:

1.  **Data Extraction**: Uses vision-capable large language models (LLMs) to scan high-resolution images of California Certificates of Title. It identifies and extracts key data points such as Manufacturer details, Serial Numbers, Decal Numbers, and Registered Owner information.
2.  **Schema Mapping**: Automatically maps extracted raw data to the specific field IDs required by various HCD forms. This phase ensures data consistency across multiple documents and formats addresses into government-compliant structures.
3.  **PDF Generation**: Programmatically fills official HCD PDF templates (476.6G, 480.5, and 476.6) using the mapped data while preserving the original document structure and layout.
4.  **Verification and Review**: Provides a web-based interface for users to preview the generated PDFs side-by-side with an editable data panel. This allows for manual corrections and instant re-generation of documents before final download.

## Technology Stack

- **Backend**: Python-based FastAPI server.
- **AI Engine**: Groq LPU (Llama 3.2 Vision for document scanning and Llama 3.3 for intelligent data mapping).
- **PDF Infrastructure**: PyMuPDF (fitz) for document rendering and pypdf for programmatic field population.
- **Frontend**: React-based dashboard with a real-time agent activity log and interactive document reviewer.

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
