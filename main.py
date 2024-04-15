from typing import List
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from connector import request_to_model


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageHistory(BaseModel):
    role: str
    skuid: str
    prompt: str

class UserMessage(BaseModel):
    messages: List[MessageHistory]
    chat_id: int = -1
    username: str = "mkrnaqeebi"
    top_p: float = 0.9
    temperature: float = 0.1
    max_tokens: int = 4000
    model: str = "gpt-35-turbo"
    proposal_model: int = 1

@app.post('/api/legal-messages', status_code=201)
def submit_message(input: UserMessage):
    print(input)
    """
    Send message to the model to get AI response
    """
    instructions = """
As an expert in legal case study. You will explain given cases dicisions according to questions. Do not add any information that is not directly relevant to the question, or not supported by the context provided. But the content is too long and too technical. The customer needs to hear a brief, actionable summary.
Respond only from the context provided.
    """
    bot_response = request_to_model(input, index='azuresql-index', project_name='Legal', instructions=instructions)
    return {"response": bot_response, "success": True}, 200





