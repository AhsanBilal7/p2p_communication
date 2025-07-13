from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from io import StringIO
from typing import Optional

from src.network import NetworkClass
from src.person import PersonClass

# Capture logs in-memory
log_stream = StringIO()
handler = logging.StreamHandler(log_stream)
handler.setLevel(logging.INFO)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="Secure Messaging API [Ahsan]",
    description="FastAPI for Project",
    version="0.1.0"
)

# Global network and participants storage
network = NetworkClass(name="Internet")
participants = {}

# Models
class Participant(BaseModel):
    name: str
    is_bad_man: Optional[bool] = False

class JoinRequest(BaseModel):
    name: str

class SendRequest(BaseModel):
    sender: str
    recipient: str
    message: str

class ExchangeKeyRequest(BaseModel):
    sender: str
    recipient: str
    sym_key: str

@app.post("/participant", summary="Create a participant")
def create_participant(p: Participant):
    if p.name in participants:
        raise HTTPException(status_code=400, detail="Participant already exists")
    person = PersonClass(name=p.name, is_bad_man=p.is_bad_man)
    participants[p.name] = person
    return {"status": "created", "name": p.name}

@app.post("/join", summary="Join the network")
def join_network(req: JoinRequest):
    person = participants.get(req.name)
    if not person:
        raise HTTPException(status_code=404, detail="Participant not found")
    network.join(person)
    return {"status": "joined", "name": req.name}

@app.post("/send", summary="Send message")
def send_message(req: SendRequest):
    sender = participants.get(req.sender)
    recipient = participants.get(req.recipient)
    if not sender or not recipient:
        raise HTTPException(status_code=404, detail="Sender or recipient not found")
    sender.send_message(recipient, req.message, network)
    return {"status": "sent", "from": req.sender, "to": req.recipient}

@app.post("/exchange", summary="Exchange symmetric key")
def exchange_key(req: ExchangeKeyRequest):
    sender = participants.get(req.sender)
    recipient = participants.get(req.recipient)
    if not sender or not recipient:
        raise HTTPException(status_code=404, detail="Sender or recipient not found")
    sender.exchange_key_with(recipient, req.sym_key, network)
    return {"status": "key_exchanged", "from": req.sender, "to": req.recipient}

@app.get("/logs", summary="Retrieve log output")
def get_logs():
    handler.flush()
    return {"logs": log_stream.getvalue().splitlines()}

@app.get("/reset", summary="Reset network and logs")
def reset():
    global network, participants
    # reset network
    network = NetworkClass(name="Internet")
    participants.clear()
    # reset logs
    log_stream.truncate(0)
    log_stream.seek(0)
    return {"status": "reset"}
