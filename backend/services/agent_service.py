"""
Author: Naisarg H.
File: services/agent_service.py
Description: This service acts as the "brain" of the application. It handles all 
interactions with the Groq AI models. It is responsible for sending scanned 
images to the vision model for extraction and using the text-based models 
to logically map that data to the correct government form fields.
"""
import os
import json
from datetime import datetime
from groq import Groq
from services.pdf_service import pdf_to_base64_images
from prompts import EXTRACTION_PROMPT, MAPPING_PROMPT

class AgentService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.vision_model = os.getenv("GROQ_VISION_MODEL")
        self.text_model = os.getenv("GROQ_TEXT_MODEL")

    def extract_data(self, file_path: str) -> dict:
        """
        Uses the AI's "eyes" to read the document. It converts the PDF into 
        pictures and asks the model to find specific labels like 'Decal Number' 
        and 'Registered Owner'.
        """
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

    def map_data(self, extracted_data: dict) -> dict:
        """
        Uses the AI's reasoning to decide where each piece of information goes.
        It looks at the names and numbers it found and chooses the correct 
        box to fill in on a specific government form.
        """
        today = datetime.now().strftime("%m/%d/%Y")
        prompt = MAPPING_PROMPT.format(
            extracted_data=json.dumps(extracted_data, indent=2), today=today
        )

        response = self.client.chat.completions.create(
            model=self.text_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=4096,
        )

        return self._parse_json(response.choices[0].message.content)

    def _parse_json(self, content: str) -> dict:
        """
        A helper function that cleans up the AI's response.
        It makes sure we only get the structured data we need, 
        discarding any extra conversational text.
        """
        content = content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback/last resort if format is raw
            return json.loads(content)
