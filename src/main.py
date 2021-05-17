from fastapi import FastAPI, Request, Response
from models import Document, database

app = FastAPI()

app.state.database = database


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
    document = await Document.objects.get(id=id)

    return Response(content=document.data, media_type="application/json")
