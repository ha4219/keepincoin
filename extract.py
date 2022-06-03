from face_parsing import execute_face_parsing, BiSeNet
from face_alignment import FaceAlignment, LandmarksType
import torch
from pydantic import BaseSettings
import os


def extract_model_feature():
  class Settings(BaseSettings):
    # TODO DOCKER inject
    KEEPMODEL: str = "/keepincoin/models"
    KEEPASSET: str = "/keepincoin/assets"
    KEEPCUDA: str = "cpu"

    class Config:
      env_file = ".env"

  settings = Settings()

  alignment = FaceAlignment(LandmarksType._3D, flip_input=False)

  torch.save(alignment, os.path.join(settings.KEEPMODEL, "face_alignment.pth"))

  WEIGHTS_PATH = "face_parsing/res/cp/79999_iter.pth"
  parsing = BiSeNet(19)
  parsing.load_state_dict(torch.load(WEIGHTS_PATH, map_location='cpu'))

  torch.save(parsing, os.path.join(settings.KEEPMODEL, 'face_parsing.pth'))


if __name__ == '__main__':
  extract_model_feature()