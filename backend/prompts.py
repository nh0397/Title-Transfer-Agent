"""
Author: Naisarg H.
File: prompts.py
Description: This file stores the instruction sets (prompts) that tell the AI
what to look for in a document and how to organize the data it finds.
There are two prompts: one for reading the title, one for mapping data to forms.
"""

EXTRACTION_PROMPT = """
You are an expert document analyst for California Manufactured Home titles.

CRITICAL FIRST STEP - DOCUMENT VALIDATION:
Before extracting anything, verify this is a valid California Certificate of Title
for a manufactured home. Look for keywords like "Department of Housing and Community
Development", "Certificate of Title", "Decal Number", or "Title Number".

If this is NOT a California Title (e.g. a resume, invoice, random document), return:
{"is_valid_title": false, "validation_error": "I appreciate the enthusiasm, but I only work with California Certificates of Title. Please upload the correct document and we will get right to it!"}

If this IS a valid title, extract EVERY piece of information and return a JSON object
with EXACTLY these keys (use empty string "" if not found):

{
  "is_valid_title": true,
  "validation_error": null,
  "manufacturer_name": "",
  "manufacturer_id": "",
  "trade_name": "",
  "model": "",
  "date_of_manufacture": "",
  "date_first_sold": "",
  "serial_number": "",
  "decal_number": "",
  "hud_label_insignia": "",
  "registered_owner_name": "",
  "registered_owner_address": "",
  "situs_address_street": "",
  "situs_address_city": "",
  "situs_address_state": "",
  "situs_address_zip": "",
  "addressee_name": "",
  "addressee_address": ""
}

IMPORTANT: Return ONLY valid JSON. No markdown, no explanation, just the JSON object.
"""

MAPPING_PROMPT = """
You are a California HCD forms specialist. Given the extracted title data and
buyer/transaction details below, create a field mapping for three government forms.

Extracted data (from the title):
{extracted_data}

Buyer and transaction details (provided by the user):
{buyer_data}

Map the data to these EXACT PDF field names. Return a JSON object with three keys:
"hcd_476_6g", "hcd_480_5", and "hcd_476_6". Each key maps to a dict of
PDF_field_name -> value.

Available field names for HCD 476.6G (Multi-Purpose Transfer Form):
- "Decal (License) No.(s) (page 1):"
- "Decal (License) No.(s) (page 2):"
- "Serial No.(s) (page 1):"
- "Serial No.(s) (page 2):"
- "Date Executed on (page 1):"
- "City and State Executed at (page 1):"
- "PHONE #:"
- "E-MAIL ADDRESS:"
- "Date Executed on (page 2):"

Available field names for HCD 480.5 (Application for Registration):
- "NEW DECAL #:" (leave blank)
- "OLD DECAL #:"
- "Name of Manufacturer:"
- "Trade Name:"
- "Date of Manufacture:"
- "Model Name or #:"
- "Date First Sold New:"
- "DECAL/LICENSE # (1):"
- "MANUFACTURER SERIAL NUMBER(S) (1)"
- "HUD LABEL OR HCD INSIGNIA # (1)"
- "Last name of Registered Owner(s) (1):"
- "First name of Registered Owner(s) (1):"
- "Middle name of Registered Owner(s) (1):"
- "Street of Current Mailing Address for Registered Owner(s):"
- "City of Current Mailing Address for Registered Owner(s):"
- "State of Current Mailing Address for Registered Owner(s):"
- "Zip of Current Mailing Address for Registered Owner(s):"
- "Street of Situs (Location) Address of unit for Registered Owner(s):"
- "City of Situs (Location) Address of unit for Registered Owner(s):"
- "State of Situs (Location) Address of unit for Registered Owner(s):"
- "Zip of Situs (Location) Address of unit for Registered Owner(s):"
- "Executed on:"
- "Executed at:"

Available field names for HCD 476.6 (Statement of Facts):
- "Trade Name:"
- "Decal (License) Number"
- "Serial Number"
- "Street Address:"
- "City:"
- "State:"
- "Statement"
- "Date Executed"
- "City Executed"
- "State Executed"
- "Printed name - 1"

Rules:
1. The Decal Number must appear on ALL three forms consistently.
2. The Serial Number must appear on ALL three forms consistently.
3. Today's date is {today}.
4. For the Statement of Facts, write a brief statement: "Transfer of ownership of the above-described manufactured home."
5. Use the registered owner name for printed name fields.
6. If buyer information is provided, use it for any buyer/new-owner fields. If not, leave them blank.
7. DO NOT remove colons (`:`) or modify the field names in any way. The JSON keys MUST exactly match the dashed list above character-for-character.
8. Leave fields blank ("") if no data is available.

Return ONLY valid JSON. No markdown, no explanation.
"""
