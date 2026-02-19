from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.rate_limit import rate_limit
from app.services.llm import get_llm_provider, StreamEvent

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatIn(BaseModel):
    message: str
    previous_response_id: str | None = None


def sse(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


@router.post("/stream", dependencies=[Depends(rate_limit("chat_stream", limit=20, window_sec=60))])
async def chat_stream(body: ChatIn):
    input_items = [
        {"role": "system", "content": "You are a helpful assistant. Be concise."},
        {"role": "user", "content": body.message},
    ]
    provider = get_llm_provider()

    def gen():
        with provider.stream_chat(
            model="gpt-4o-mini",
            input_items=input_items,
            previous_response_id=body.previous_response_id,
        ) as stream:
            for event in stream:
                if event.kind == "delta" and event.text:
                    yield sse("delta", event.text)
                elif event.kind == "done" and event.response_id:
                    yield sse("done", event.response_id)

    return StreamingResponse(gen(), media_type="text/event-stream")