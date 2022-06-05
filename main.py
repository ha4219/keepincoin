from typing import Union

from fastapi import FastAPI, Form, File, UploadFile
from pydantic import BaseSettings
import torch
import os

from face_parsing.face_parsing import _execute_face_parsing

class Settings(BaseSettings):
  # TODO DOCKER inject
  KEEPMODEL: str = "/keepincoin/models"
  KEEPASSET: str = "/keepincoin/assets"
  KEEPCUDA: str = "cpu"

  class Config:
    env_file = ".env"

settings = Settings()

app = FastAPI()


# TODO #2 FEAT connect torch model(face_alignment, face_parsing) by cpu

alignment = torch.load(os.path.join(settings.KEEPMODEL, 'face_alignment.pth')).face_alignment_net.to(settings.KEEPCUDA)
parsing = torch.load(os.path.join(settings.KEEPMODEL, 'face_parsing.pth')).to(settings.KEEPCUDA)


def execute_alignment(img, dst):
  import numpy as np
  np.array(alignment.get_landmarks(img)).tofile(dst)

def execute_parsing(img, dst):
  _execute_face_parsing(dst, img, parsing, settings.KEEPCUDA)

# TODO #1 FEAT post backbone function

@app.get('/')
def read_root():
  return {"Hello": "World"}


