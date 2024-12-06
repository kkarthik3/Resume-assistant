from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from src.dataload.app import main as refresh_data
import os
import uvicorn
from pydantic import BaseModel
from src.langgraph_structure import lang_app

app = FastAPI()
security = HTTPBasic()

# Authentication function
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("API_USERNAME")
    correct_password = os.getenv("API_PASSWORD")
    if not (credentials.username == correct_username and credentials.password == correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials

# Define the input model for the query
class QueryRequest(BaseModel):
    message: str
    chatid : str

_printed = set()

def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)
            return event
        
# Endpoint for querying the chatbot
@app.post("/query")
def query_endpoint(query: QueryRequest, credentials: HTTPBasicCredentials = Depends(authenticate)):
    config = {"configurable": {"thread_id": query.chatid}}
    events = lang_app.stream({"messages": ("user", query.message)}, config, stream_mode="values")
    for event in events:
        _print_event(event, _printed)

    snapshot = lang_app.get_state(config=config)

    print(snapshot)
    responses = snapshot.values
    return{"message": snapshot.values["messages"][-1].content}


# Endpoint to refresh the data
@app.get("/refresh")
def refresh_endpoint(credentials: HTTPBasicCredentials = Depends(authenticate)):
    try:
        refresh_data()
        return {"message": "Data refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error refreshing data")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000,reload=True)
