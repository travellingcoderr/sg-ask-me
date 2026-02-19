from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def create_response_stream(model: str, input_items: list, previous_response_id: str | None = None):
    return client.responses.stream(
        model=model,
        input=input_items,
        previous_response_id=previous_response_id,
    )