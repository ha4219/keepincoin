from typing import Union

from fastapi import FastAPI, Form, File, UploadFile

app = FastAPI()


@app.get('/')
def read_root():
  return {"Hello": "World"}
