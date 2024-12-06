from pydantic import BaseModel
from langchain.prompts import ChatPromptTemplate

from apis.dbconnection import connect_to_mongo
from apis.model import model
from src.mongorag.query import get_details

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

#initialize the mongo connection
client,collection  = connect_to_mongo()

# Mongo agent for RAG
mongo_rag_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "  ** Main Tasks ** "
            "You are a helpful assistant answer the user queries with help of mongo_retrive_tool. "
            "Pass the Exact User Query including the Question words to the tool without any change"

            "** Do not do's** "
            "should not remove the Question Words from the user Query "
            "Do not answer too much and don't give long answers. "
            "do not answer the user queries that are not related to the mongo_retrive_tool. "
            "Do not generate the answers that are not related to the mongo_retrive_tool. "
            "Do not answer the user queries when get irrelevants from the mongo_retrive_tool. "
        ),
        (
            "placeholder",
            "{messages}"
        ),
    ]
)

mongo_rag_tool = [get_details]
mongo_rag_runnable = mongo_rag_prompt_template | model.bind_tools(mongo_rag_tool + [CompleteOrEscalate],tool_choice="auto")
