import datetime

from hashlib import sha512

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from epserver.models import Document, database

from ormar.exceptions import NoMatch, MultipleMatches

spa_url = "https://engineeringpaper.xyz"

app = FastAPI()

app.state.database = database

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    data = await request.body()
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
        document = Document(data=data, data_hash=data_hash)
        await document.save()
    
    return {"url":f"{spa_url}/#{document.id}", "hash":document.id}


@app.get("/documents/{id}")
async def get_document(id):
    try:
        document = await Document.objects.get(id=id)
    except NoMatch:
        raise HTTPException(status_code=404, detail="Document not found")

    document.num_reads += 1
    document.access = datetime.datetime.now()

    await document.update()

    return Response(content=document.data, media_type="application/json")
