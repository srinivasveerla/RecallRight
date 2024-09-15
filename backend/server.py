from typing import Union

from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/data")
async def read_root(request: Request):
    # Parse the incoming request body
    body = await request.body()
    print(body.decode())  # Print the raw body (decode to convert bytes to string)
    return {"message": "Data received successfully"}
