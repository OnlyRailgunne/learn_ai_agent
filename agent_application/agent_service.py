from collections.abc import Iterator

from pydantic import BaseModel
from langgraph.types import Command

from agent_application.langgraph_agent import graph


class AgentInput(BaseModel):
    message: str
    messages: list


class AgentEvent(BaseModel):
    type: str
    content: str | None = None
    tool: str | None = None
    arguments: str | None = None
    error_type: str | None = None


class AgentResponse(BaseModel):
    message: str


def stream_agent(
    agent_input: AgentInput,
    final_result: dict,
    thread_id: str,
) -> Iterator[AgentEvent]:

    messages = agent_input.messages + [
        {
            "role": "user",
            "content": agent_input.message,
        }
    ]

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    try:
        for mode, event in graph.stream(
            {
                "messages": messages,
                "tool_calls": [],
            },
            config=config,
            stream_mode=["custom", "values"],
        ):
            if mode == "custom":
                yield AgentEvent(
                    type=event["type"],
                    content=event.get("content"),
                    tool=event.get("tool"),
                    arguments=event.get("arguments"),
                )

            elif mode == "values":

                if "__interrupt__" in event:

                    interrupt_info = event["__interrupt__"][0]
                    approval = interrupt_info.value

                    final_result["waiting_approval"] = True
                    final_result["tool"] = approval["tool"]
                    final_result["arguments"] = approval["arguments"]

                    yield AgentEvent(
                        type="approval_required",
                        tool=approval["tool"],
                        arguments=str(approval["arguments"]),
                    )

                    return

                final_result["messages"] = event["messages"]

                if event["messages"]:
                    last_message = event["messages"][-1]

                    if last_message.get("role") == "assistant":
                        final_result["response"] = AgentResponse(
                            message=last_message.get("content", "")
                        )

        response = final_result.get("response")

        if response is not None:
            yield AgentEvent(
                type="done",
                content=response.message,
            )
        else:
            yield AgentEvent(
                type="done",
            )

    except Exception as e:
        yield AgentEvent(
            type="error",
            content=str(e),
            error_type="agent_error",
        )


def resume_agent(
    thread_id: str,
    approved: bool,
    final_result: dict,
) -> Iterator[AgentEvent]:

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    try:
        for mode, event in graph.stream(
            Command(resume=approved),
            config=config,
            stream_mode=["custom", "values"],
        ):
            if mode == "custom":
                yield AgentEvent(
                    type=event["type"],
                    content=event.get("content"),
                    tool=event.get("tool"),
                    arguments=event.get("arguments"),
                )

            elif mode == "values":

                if "__interrupt__" in event:
                    interrupt_info = event["__interrupt__"][0]
                    approval = interrupt_info.value

                    final_result["waiting_approval"] = True

                    yield AgentEvent(
                        type="approval_required",
                        tool=approval["tool"],
                        arguments=str(approval["arguments"]),
                    )

                    return

                final_result["messages"] = event["messages"]

                if event["messages"]:
                    last_message = event["messages"][-1]

                    if last_message.get("role") == "assistant":
                        final_result["response"] = AgentResponse(
                            message=last_message.get("content", "")
                        )

        response = final_result.get("response")

        if response is not None:
            yield AgentEvent(
                type="done",
                content=response.message,
            )
        else:
            yield AgentEvent(
                type="done",
            )

    except Exception as e:
        yield AgentEvent(
            type="error",
            content=str(e),
            error_type="agent_error",
        )