import json
import datetime
from typing import List, Dict

from hashlib import sha512

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from epserver.models import Document, database

import pydantic

import ormar
from ormar.exceptions import NoMatch, MultipleMatches

spa_url = "https://engineeringpaper.xyz"

app = FastAPI(docs_url=None, redoc_url=None)

app.state.database = database

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class DocumentPostRequest(pydantic.BaseModel):
    title: str
    document: str
    history: List[Dict[str, str]]


class DocumentPostReponse(pydantic.BaseModel):
    url: str
    hash: str
    history: str

class DocumentGetReponse(pydantic.BaseModel):
    data: str
    history: str

@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.post("/documents/{request_hash}")
async def create_document(request_hash, request: DocumentPostRequest):
    title = request.title
    data = request.document.encode('utf-8')
    data_hash = sha512(b' '+data+b'math').hexdigest()

    if (data_hash != request_hash):
        raise HTTPException(status_code=404, detail="Document not found.")

    data = data.decode('utf-8')

    try:
        document = await Document.objects.get(data_hash=data_hash)

        if data != document.data:
            # hash collision
            raise NoMatch('Not found')

    except (NoMatch, MultipleMatches):
        history = request.history
        document = Document(data=data, data_hash=data_hash,
                            title=title, history=history)
        await document.save()

        document.history.insert(0, {"url": f"{spa_url}/#{document.id}",
                                    "creation": f"{document.creation.isoformat()}Z"})
        await document.update()
    
    return DocumentPostReponse(url=f"{spa_url}/#{document.id}",
                               hash=document.id,
                               history=json.dumps(document.history))


@app.get("/documents/{id}")
async def get_document(id):
    try:
        document = await Document.objects.get(id=id)
    except NoMatch:
        raise HTTPException(status_code=404, detail="Document not found")

    document.num_reads += 1
    document.access = datetime.datetime.utcnow()

    await document.update()

    return DocumentGetReponse(data=document.data,
                              history=json.dumps(document.history))
