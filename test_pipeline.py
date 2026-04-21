import json
from dotenv import load_dotenv
load_dotenv("backend/.env")
from services.agent_service import AgentService

agent = AgentService()
extracted = agent.extract_data("data/Title Transfer Documents.pdf")
print("Extracted:")
print(json.dumps(extracted, indent=2))

mapped = agent.map_data(extracted)
print("Mapped:")
print(json.dumps(mapped, indent=2))
