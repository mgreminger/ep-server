import datetime

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Document, database

from ormar.exceptions import NoMatch

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


@app.post("/documents/")
async def create_document(request: Request):
    data = await request.body()
    document = Document(data=data)
    await document.save()

    return {"id":document.id}


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
