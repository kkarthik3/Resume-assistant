from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from datetime import datetime
import pytz
from typing import Optional
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
from src.primary_agent.personal import personal_details
from apis.model import model
load_dotenv()

class RagAssistant(BaseModel):
    """Transfer to RAG assistant whenever the user requests query based on proffesional questions without changing the user query. Don't change the user query."""
    question:str = Field(None, description="Exact content in HumanMessage")


@tool
def current_datetime_info() -> Optional[str]:
    """
    Returns the current date, time, and day in the format DD-MM-YYYY HH:MM:SS (Day) for Indian Standard Time (IST).

    Returns:
        Optional[str]: The current date, time, and day in the format DD-MM-YYYY HH:MM:SS (Day),
                       or None if an error occurs.
    """
    try:
        ist_timezone = pytz.timezone("Asia/Kolkata")
        current_time = datetime.now(ist_timezone)
        formatted_time = current_time.strftime("%d-%m-%Y %H:%M:%S (%A)")
        return formatted_time
    except Exception:
        return None

# Example usage
# print(current_datetime_info())


primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            " **Objectives** "
            "you are a helpful chat assistant for Karthikeyan"
            "you must simply pass the exact user query whatever to the RagAssistant without changing or modifying or adding or makeup the user query other than passing. "
            "For Example, if the user ask *what is your name* pass the exact Query as *what is your name*"
            "you need to delegate user queries like *wh* Questions to the RagAssistant whenever the user asks queries other than chit chat."
            "your primary role is to answer only the chit chat questions asked by the user like greetings and goodbyes. "
            "The user is unaware of these specialized assistants, so do not mention them. Simply handle the delegation quietly. "
            "you should not answer anything else other than the chit chat questions like greetings and goodbyes."
            "You are able to answer the current date and time whenever the user asks for it using the current_datetime_info tools."
            "If the user uses 'You' or 'Your,' they are referring to Karthikeyan."
            "If the user enquires about your personal details like, Dob, work experience, current employer, expected salary,address,contact and communication and language profficieny etc. use the personal_details_tools to get the details",
        ),
        (
            "placeholder",
            "{messages}"
        ),
    ]
)
primary_agent_tools = [current_datetime_info]
personal_details_tool = [personal_details]
primary_assistant_runnable = primary_assistant_prompt | model.bind_tools(primary_agent_tools+[RagAssistant]+personal_details_tool)