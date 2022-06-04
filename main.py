'''
main fastapi
'''
import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import torch
import numpy as np
import cv2

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

def load_image_into_numpy_array(data):
	''' fastapi image file to numpy image'''
	npimg = np.frombuffer(data, np.uint8)
	frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
	cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	return frame

# TODO(ha4219): #1 FEAT post backbone function

@app.get('/')
def read_root():
	'''
	url / test
	'''
	return {"Hello": "World"}


@app.post('/uploader')
async def uploader(
		front: UploadFile = File(None),
		text: UploadFile = File(None),
		back: UploadFile = File(None),
		back_text: UploadFile = File(None),
		style: str = Form("chram"),
		shape: str = Form("circle"),
		border: str = Form("basic"),
		embo: bool = Form(False),
		emboline: bool = Form(False),
	):
	'''
	basic logic

	Parameters
	-----------
		front: UploadFile
			앞면 이미지
		text: UploadFile
			앞면 텍스트 파일
		back: UploadFile
			뒷면 이미지
		back_text: UploadFile
			뒷면 텍스트 파일
		style: str
			charm(참) - default
			frame(프레임)
		shape: str
			circle(원형) - default
			square(사각)
			ellipse(타원)
			octagon(팔각)

		border: str
			basic(기본) - default
			bead(구슬)
			twist(꽈배기)
			curve(굴곡)

		embo: str
			true(엠보)
			false(민자) - default

		emboline: str
			엠보라인 - 기본배경*embo-false시에 추가가능
			true(추가)
			false(추가하지않음) - default
	Return
	---------
		res: json
		return saved path
	'''
	if not front:
		raise HTTPException(status_code=517, detail="front parameter is required.")
	front = load_image_into_numpy_array(await front.read())
	front_text = load_image_into_numpy_array(await text.read())
	back = load_image_into_numpy_array(await back.read())
	back_text = load_image_into_numpy_array(await back_text.read())

	try:
		execute_alignment(front, "")
	except Exception as exc:
		raise HTTPException(status_code=518, detail="alignment error") from exc
	try:
		execute_parsing(front, "")
	except Exception as exc:
		raise HTTPException(status_code=519, detail="parsing error") from exc

	return {}
