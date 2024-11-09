from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app import main as refresh_data
from query import generate_rag_response
import os
import uvicorn
from pydantic import BaseModel

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

ids = []
#session
def is_new_session(chatid: str) -> bool:
    if chatid not in ids:
        ids.append(chatid)
        if len(ids) > 3:
            ids.pop(0)
        return True
    return False
    
# Endpoint for querying the chatbot
@app.post("/query")
def query_endpoint(query: QueryRequest, credentials: HTTPBasicCredentials = Depends(authenticate)):
    try:
        response = generate_rag_response(user_query=query.message, refresh=is_new_session(query.chatid))
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
