"""
Author: Naisarg H.
File: services/agent_service.py
Description: This is the brain of the application. It talks to either a cloud AI
(Groq) or a local AI (Ollama) depending on the USE_LOCAL_AI setting in the
environment file. It sends scanned title images for data extraction and then
asks the AI to map that data onto government form fields.
"""
import os
import json
import base64
from datetime import datetime
from groq import Groq
from services.pdf_service import pdf_to_base64_images
from prompts import EXTRACTION_PROMPT, MAPPING_PROMPT

# Only import ollama if available
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class AgentService:
    """Handles all AI interactions for the title transfer pipeline."""

    def __init__(self):
        self.use_local = os.getenv("USE_LOCAL_AI", "false").lower() == "true"
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma4")

        # Cloud config (Groq) — always initialize as fallback
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.vision_model = os.getenv("GROQ_VISION_MODEL")
        self.text_model = os.getenv("GROQ_TEXT_MODEL")

    def extract_data(self, file_path: str) -> dict:
        """
        Reads a title document by converting it to an image and sending it
        to the AI. Uses local Ollama if the flag is set, otherwise uses cloud.
        """
        if self.use_local and OLLAMA_AVAILABLE:
            return self._extract_local(file_path)
        return self._extract_cloud(file_path)

    def map_data(self, extracted_data: dict, buyer_data: dict = None) -> dict:
        """
        Takes the raw extracted data and figures out which box on which
        government form each piece of information belongs to.
        """
        if self.use_local and OLLAMA_AVAILABLE:
            return self._map_local(extracted_data, buyer_data)
        return self._map_cloud(extracted_data, buyer_data)

    # ── Cloud Methods (Groq API) ──

    def _extract_cloud(self, file_path: str) -> dict:
        """Sends the document image to Groq's cloud vision model."""
        page_images = pdf_to_base64_images(file_path)

        content = [{"type": "text", "text": EXTRACTION_PROMPT}]
        for img_b64 in page_images:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"}
            })

        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[{"role": "user", "content": content}],
            temperature=0,
            max_tokens=2048,
        )
        return self._parse_json(response.choices[0].message.content)

    def _map_cloud(self, extracted_data: dict, buyer_data: dict = None) -> dict:
        """Sends extracted data to Groq's cloud text model for mapping."""
        today = datetime.now().strftime("%m/%d/%Y")
        buyer_str = json.dumps(buyer_data, indent=2) if buyer_data else "No additional buyer information provided."
        prompt = MAPPING_PROMPT.format(
            extracted_data=json.dumps(extracted_data, indent=2), 
            buyer_data=buyer_str,
            today=today
        )

        response = self.client.chat.completions.create(
            model=self.text_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=4096,
        )
        return self._parse_json(response.choices[0].message.content)

    # ── Local Methods (Ollama) ──

    def _extract_local(self, file_path: str) -> dict:
        """Sends the document image to the local Ollama vision model."""
        page_images = pdf_to_base64_images(file_path)
        images_bytes = [base64.b64decode(img) for img in page_images]

        response = ollama.chat(
            model=self.ollama_model,
            messages=[{
                "role": "user",
                "content": EXTRACTION_PROMPT,
                "images": images_bytes,
            }],
        )
        return self._parse_json(response["message"]["content"])

    def _map_local(self, extracted_data: dict, buyer_data: dict = None) -> dict:
        """Sends extracted data to local Ollama for field mapping."""
        today = datetime.now().strftime("%m/%d/%Y")
        buyer_str = json.dumps(buyer_data, indent=2) if buyer_data else "No additional buyer information provided."
        prompt = MAPPING_PROMPT.format(
            extracted_data=json.dumps(extracted_data, indent=2), 
            buyer_data=buyer_str,
            today=today
        )

        response = ollama.chat(
            model=self.ollama_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_json(response["message"]["content"])

    # ── Helpers ──

    def _parse_json(self, content: str) -> dict:
        """
        Cleans up the AI response to extract only the JSON data,
        stripping away any markdown formatting the model may add.
        """
        content = content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
