import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent_application.agent_service import (
    AgentInput,
    resume_agent,
    stream_agent,
)
from agent_application.session_store import SessionStore


app = FastAPI()

session_store = SessionStore()


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ApprovalRequest(BaseModel):
    session_id: str
    approved: bool


@app.get("/")
def home():
    return {
        "message": "Agent API is running"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    session_id = request.session_id

    lock = session_store.get_lock(session_id)

    final_result = {}

    def generate():

        try:
            with lock:

                messages = session_store.get(session_id)

                agent_input = AgentInput(
                    message=request.message,
                    messages=messages,
                )

                for event in stream_agent(
                    agent_input,
                    final_result,
                    session_id,
                ):
                    yield (
                        "data: "
                        + json.dumps(
                            event.model_dump(),
                            ensure_ascii=False,
                        )
                        + "\n\n"
                    )

                if "messages" in final_result:
                    session_store.save(
                        session_id,
                        final_result["messages"],
                    )

        except GeneratorExit:
            return

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@app.post("/approval")
def approval(request: ApprovalRequest):

    session_id = request.session_id

    lock = session_store.get_lock(session_id)

    final_result = {}

    def generate():

        try:
            with lock:

                for event in resume_agent(
                    thread_id=session_id,
                    approved=request.approved,
                    final_result=final_result,
                ):
                    yield (
                        "data: "
                        + json.dumps(
                            event.model_dump(),
                            ensure_ascii=False,
                        )
                        + "\n\n"
                    )

                if "messages" in final_result:
                    session_store.save(
                        session_id,
                        final_result["messages"],
                    )

        except GeneratorExit:
            return

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )