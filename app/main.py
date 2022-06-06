'''
main fastapi
'''
import os
import io
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import torch
import numpy as np
from PIL import Image

from app.config import Settings
from app.face_parsing.face_parsing import _execute_face_parsing

settings = Settings()

app = FastAPI()

alignment = torch.load(os.path.join(settings.KEEPMODEL, 'face_alignment.pth'))
parsing = torch.load(os.path.join(settings.KEEPMODEL, 'face_parsing.pth')).to(settings.KEEPCUDA)

def execute_alignment(img, dst: str):
    '''
    run alignment
    '''
    np.array(alignment.get_landmarks(np.array(img))).tofile(dst)

def execute_parsing(img, dst: str):
    '''
    run parsing
    '''
    _execute_face_parsing(dst, img, parsing, settings.KEEPCUDA)

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
    -----------
        res: json
        return saved path
    '''
    if not front:
        raise HTTPException(status_code=517, detail="front parameter is required.")
    front = Image.open(io.BytesIO(await front.read())).convert('RGB')
    front_text = Image.open(io.BytesIO(await front_text.read())).convert('RGB') \
        if text else 'NONE'
    back = Image.open(io.BytesIO(await back.read())).convert('RGB') \
        if back else 'NONE'
    back_text = Image.open(io.BytesIO(await back_text.read())).convert('RGB') \
        if back_text else 'NONE'

    try:
        execute_alignment(front, "test.bin")
    except Exception as exc:
        raise HTTPException(status_code=518, detail="alignment error") from exc
    try:
        execute_parsing(front, "test.png")
    except Exception as exc:
        raise HTTPException(status_code=519, detail="parsing error") from exc


    return {'style': style, 'shape': shape, 'border': border, 'embo': embo, 'emboline': emboline}
