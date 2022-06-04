'''
des
'''
import os
from fastapi import FastAPI
import torch
import numpy as np
from config import Settings

from face_parsing.face_parsing import _execute_face_parsing


settings = Settings()

app = FastAPI()


# TODO(ha4219): #2 FEAT connect torch model(face_alignment, face_parsing) by cpu

alignment = torch.load(os.path.join(settings.KEEPMODEL, 'face_alignment.pth'))\
	.face_alignment_net.to(settings.KEEPCUDA)
parsing = torch.load(os.path.join(settings.KEEPMODEL, 'face_parsing.pth')).to(settings.KEEPCUDA)


def execute_alignment(img, dst: str):
	'''
	run alignment
	'''
	np.array(alignment.get_landmarks(img)).tofile(dst)

def execute_parsing(img, dst: str):
	'''
	run parsing
	'''
	_execute_face_parsing(dst, img, parsing, settings.KEEPCUDA)

# TODO(ha4219): #1 FEAT post backbone function

@app.get('/')
def read_root():
	'''
	url / test
	'''
	return {"Hello": "World"}
