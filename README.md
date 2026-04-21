# Title Transfer Agent

The Title Transfer Agent is an automated system designed to streamline the processing and transfer of manufactured home titles within California. It utilizes multimodal artificial intelligence to extract data from official scanned documents and programmatically populates the corresponding government forms required by the California Department of Housing and Community Development (HCD).

## How It Works

The system operates in four straightforward steps:

1. **Upload & Scan**: You upload a California Certificate of Title (PDF). The AI (vision model) scans it and extracts key information (Decal number, Serial number, Manufacturer, Owner).
2. **Buyer Info Entry**: (Optional) You can manually input the new Buyer's name, address, and sale price in the dashboard.
3. **Smart Mapping & Filling**: The AI maps the extracted title data and your manual buyer data to the exact required fields across three official government forms (HCD 476.6G, 480.5, and 476.6). Python scripts then physically fill the PDF forms.
4. **Review & Download**: The dashboard displays a preview of the forms. You can edit any mistakes inline and re-generate. Finally, you can download all forms merged into one complete "Transfer Packet".

## Technology Stack & Design Decisions

- **Backend**: Python + FastAPI. Chosen to easily interface with Python's robust AI and PDF libraries (`pypdf`, `PyMuPDF`).
- **Frontend**: React.
- **AI**: Built to support both Cloud (Groq) for speed and Local (Ollama) for privacy.

### Scaling Limitation Note
Attempting to handle more complex or larger documents just by throwing a larger "billion-parameter" model at it creates massive latency blocks in synchronous web requests. Fine-tuned deterministic logic alongside smaller fast models scales better for highly structured text extraction.

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
