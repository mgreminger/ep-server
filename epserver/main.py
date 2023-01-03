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
max_size = 2000000 # max length of byte string that represents sheet

app = FastAPI(docs_url=None, redoc_url=None)

app.state.database = database

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:8788", "https://engineeringpaper.xyz"],
    allow_origin_regex="https://.*\.engineeringpaper\.pages\.dev",
    allow_methods=["*"],
    allow_headers=["*"]
)


class DocumentPostResponse(pydantic.BaseModel):
    url: str
    hash: str
    history: str

class DocumentGetResponse(pydantic.BaseModel):
    data: str
    history: str

class DeleteTestSheetsResponse(pydantic.BaseModel):
    numRowsDeleted: int

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
async def create_document(request_hash, request: Request):
    request_dict = json.loads(await request.body())

    title = request_dict['title']
    data = request_dict['document'].encode('utf-8')
    data_hash = sha512(b' '+data+b'math').hexdigest()

    if (data_hash != request_hash):
        raise HTTPException(status_code=404, detail="Document not found.")

    data = data.decode('utf-8')

    try:
        if len(request_dict['history']) == 0:
            # document has never been saved, no point checking
            raise NoMatch('Not found')

        document = await Document.objects.get(data_hash=data_hash)

        if request_dict['history'][0]['hash'] != document.id:
            # matching document with different history, create new document
            raise NoMatch('Not found')

        if data != document.data:
            # hash collision, create new document
            raise NoMatch('Not found')

    except (NoMatch, MultipleMatches):
        history = request_dict['history']

        if len(data) > max_size:
            raise HTTPException(status_code=413, detail="Sheet too large for database, reduce size of images in documentation cells.")

        document = Document(data=data, data_hash=data_hash,
                            title=title, history=history,
                            creation_ip=request.client.host)
        await document.save()

        document.history.insert(0, {"url": f"{spa_url}/#{document.id}",
                                    "hash": document.id,
                                    "creation": f"{document.creation.isoformat()}Z"})
        await document.update()

    return DocumentPostResponse(url=f"{spa_url}/#{document.id}",
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

    return DocumentGetResponse(data=document.data,
                              history=json.dumps(document.history))


@app.put("/delete_test_sheets")
async def delete_test_sheets():
    try:
        num_rows_deleted = await Document.objects.delete(title='Title for testing purposes only, will be deleted from database automatically')
    except NoMatch:
        # nothing needs to be done, no test sheets in database
        return DeleteTestSheetsResponse(numRowsDeleted = 0)

    return DeleteTestSheetsResponse(numRowsDeleted = num_rows_deleted)

    