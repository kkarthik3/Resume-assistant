from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda
from langchain_core.messages import ToolMessage, AnyMessage, AIMessage, HumanMessage, SystemMessage, RemoveMessage
from typing import Annotated, Literal, TypedDict, Optional, Callable
from pydantic import BaseModel
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool


#agents
from src.primary_agent.primary_agent import primary_assistant_runnable,primary_agent_tools,RagAssistant,personal_details_tool
from src.mongorag.mongo_agent import mongo_rag_runnable,mongo_rag_tool

def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """Push or pop the state."""
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    summary: str
    user_info: str
    dialog_state: Annotated[
        list[
            Literal[
                "primary_assistant",
                "rag_assistant",
                "Self_assistant",
            ]
        ],
        update_dialog_stack,
    ]

class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the user's needs."""

    cancel: bool = True
    reason: str
    class Config:
        json_schema_extra = {
            "example": {
                "cancel": True,
                "reason": "User changed their mind about the current task.",
            },
            "example 2": {
                "cancel": True,
                "reason": "I have fully completed the task.",
            },
            "example 3": {
                "cancel": False,
                "reason": "I need to search the emails for more information.",
            },
        }
def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks([RunnableLambda(handle_tool_error)], exception_key="error")

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            result = self.runnable.invoke(state)
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                messages = state["messages"][-3] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
                messages = state["messages"][-3] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                break
        return {"messages": result}
    

def create_entry_node(assistant_name: str, new_dialog_state: str) -> Callable:
    def entry_node(state: State) -> dict:
        tool_call_id = state["messages"][-1].tool_calls[0]["id"]
        return {
            "messages": [
                ToolMessage(
                    content=f"The assistant is now the {assistant_name}. Reflect on the above conversation between the host assistant and the user."
                    f" The user's intent is unsatisfied. Use the provided tools to assist the user. Remember, you are {assistant_name},"
                    " and the create, update, other other action is not complete until after you have successfully invoked the appropriate tool."
                    " If the user changes their mind or needs help for other tasks, call the CompleteOrEscalate function to let the primary host assistant take control."
                    " Do not mention who you are - just act as the proxy for the assistant.",
                    tool_call_id=tool_call_id,
                )
            ],
            "dialog_state": new_dialog_state,
        }

    return entry_node


def pop_dialog_state(state: State) -> dict:
    """Pop the dialog stack and return to the main assistant.

    This lets the full graph explicitly track the dialog flow and delegate control
    to specific sub-graphs.
    """
    messages = []
    if state["messages"][-1].tool_calls:
        messages.append(
            ToolMessage(
                content="Resuming dialog with the host assistant. Please reflect on the past conversation and assist the user as needed.",
                tool_call_id=state["messages"][-1].tool_calls[0]["id"],
            )
        )
    return {
        "dialog_state": "pop",
        "messages": messages,
    }   


builder = StateGraph(State)

#primary assistant 
builder.add_node("primary_assistant", Assistant(primary_assistant_runnable))
builder.add_node("primary_agent_tools", create_tool_node_with_fallback(primary_agent_tools))
builder.add_edge(START, "primary_assistant")
builder.add_edge("primary_agent_tools", "primary_assistant")

builder.add_node("personal_details_tool", create_tool_node_with_fallback(personal_details_tool))
builder.add_edge("personal_details_tool", "primary_assistant")

builder.add_node("leave_skill", pop_dialog_state)
builder.add_edge("leave_skill", "primary_assistant")

builder.add_node("enter_rag_assistant", create_entry_node("RagAssistant", "mongo_agent"))
builder.add_node("mongo_agent", Assistant(mongo_rag_runnable))
builder.add_node("rag_agent",create_tool_node_with_fallback(mongo_rag_tool))

builder.add_edge("enter_rag_assistant", "mongo_agent")
builder.add_edge("rag_agent", END)


def route_primary_assistant(
    state: State,
) -> Literal[
    "primary_agent_tools",
    "enter_rag_assistant",
    "personal_details_tool"

]:
    route = tools_condition(state)
    if route == END:
        return END
    
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls:
        if tool_calls[0]["name"] == RagAssistant.__name__:
            return "enter_rag_assistant"
        elif tool_calls[0]["name"] == "personal_details":
            return "personal_details_tool"
        else:
            return "primary_agent_tools"

    raise ValueError("Invalid route")

def route_rag_agent(
    state: State,
) -> Literal[
    "leave_skill"]:


    route = tools_condition(state)
    
    tool_calls = state["messages"][-1].tool_calls
    did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)
    
    if did_cancel:
        return "leave_skill"
    
    if tool_calls:
        if tool_calls[0]["name"] == "get_details":
            return "rag_agent"


    raise ValueError("Invalid route")


builder.add_conditional_edges(
    "primary_assistant",
    route_primary_assistant,
    {
        "enter_rag_assistant": "enter_rag_assistant",
        "primary_agent_tools": "primary_agent_tools",
        "personal_details_tool": "personal_details_tool",
        END:END
    },
)

builder.add_conditional_edges(
    "mongo_agent",
    route_rag_agent,
    {
        "leave_skill": "leave_skill",
        "rag_agent": "rag_agent"

    },
)


memory = MemorySaver()
lang_app = builder.compile(checkpointer=memory)

lang_app.get_graph(xray=True).draw_mermaid_png(output_file_path="graph.png")