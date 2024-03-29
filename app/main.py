"""
main fastapi
"""
from enum import Enum, unique
import os
import platform
import io
import ctypes
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
import torch
import numpy as np
from PIL import Image

from app.config import Settings
from app.face_parsing.face_parsing import _execute_face_parsing
from app.coin_generator.generator import generate_coin
from app.path_util import now_to_str


settings = Settings()

VERSION = "0.0.47"

TARGET = 218

app = FastAPI(
    title="keepincoin",
    version=VERSION,
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['*'],
#     allow_credentials=True,
#     allow_methods=['*'],
#     allow_headers=['*'],
# )

mapping = {
    'Windows': '',
    'Linux': 'lib_ubuntu.so',
    'Darwin': 'lib_mac.so'
}

@unique
class Border(str, Enum):
    '''
        border category
    '''
    BASIC = "basic"
    BALLS = "balls"
    CURVED = "curved"
    TWISTED = "twisted"

# @unique
# class ImgType(str, Enum):
#     '''
#         img type
#     '''
#     IMAGE = 'image'
#     ILLUST = 'illust'

alignment = torch.load(os.path.join(settings.KEEPMODEL, 'face_alignment.pth'))
parsing = torch.load(os.path.join(settings.KEEPMODEL, 'face_parsing.pth')).to(settings.KEEPCUDA)
lib = ctypes.cdll.LoadLibrary(os.path.join(settings.KEEPMODEL, mapping[platform.system()]))

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
async def read_root():
    '''
    url / test
    '''
    return {
        "version": VERSION
    }

@app.post('/uploader')
async def uploader(
        front: UploadFile = File(None),
        text: UploadFile = File(None),
        back: UploadFile = File(None),
        back_text: UploadFile = File(None),
        border: Border = Form("basic"),
        is_pad_front: bool = Form(False),
        is_pad_back: bool = Form(False),
        is_face_in_front: bool = Form(True),
	):
    """
    basic logic

    Parameters
    -----------
        front: UploadFile - Required
            앞면 이미지
        text: UploadFile
            앞면 텍스트 파일
        back: UploadFile
            뒷면 이미지
        back_text: UploadFile
            뒷면 텍스트 파일
        *border: str - Required*
            basic(기본) - default
            balls(구슬)
            twisted(꽈배기)
            curved(굴곡)
        is_pad_front: bool
            앞면 테두리쪽 여백 여부
            false - default
            true
        is_pad_back: bool
            뒷면 테두리쪽 여백 여부
            false - default
            true

    Return
    -----------
        "front_image_path": 앞면 이미지 파일 위치,
        "back_image_path": 뒷면 이미지 파일 위치 없을 경우 null,
        "coin_dst_path": { coin 위치 path, naming_rule: size_options..., 아래는 예시입니다.
            "15_dual" : f"/assets/{now}/coins/coin_15_{border}_dual.stl",
            "15" : f"/assets/{now}/coins/coin_15_{border}.stl",

            "18_dual" : f"/assets/{now}/coins/coin_18_{border}_dual.stl",
            "18" : f"/assets/{now}/coins/coin_18_{border}.stl",

            "21_dual" : f"/assets/{now}/coins/coin_21_{border}_dual.stl",
            "21" : f"/assets/{now}/coins/coin_21_{border}.stl",
        }
    """
    if not front:
        raise HTTPException(status_code=517, detail="front parameter is required.")
    front = Image.open(io.BytesIO(await front.read())).convert('RGB')
    front_width, front_height = front.size
    margin_x = (front_width - TARGET) // 2
    margin_y = (front_height - TARGET) // 2
    if margin_x >= 0 and margin_y >= 0:
        front = front.crop((margin_x, margin_y, margin_x + TARGET, margin_y + TARGET))
    front = front.resize((512, 512))

    front_text = Image.open(io.BytesIO(await text.read())).convert('RGB').resize((512, 512)) \
        if text else None
    back = Image.open(io.BytesIO(await back.read())).convert('RGB').resize((512, 512)) \
        if back else None
    back_text = Image.open(io.BytesIO(await back_text.read())).convert('RGB').resize((512, 512)) \
        if back_text else None

    now = now_to_str()
    res_path = f"{settings.KEEPSTATIC}/{now}"
    coin_path = f"{res_path}/coins"
    os.mkdir(res_path)
    os.mkdir(coin_path)

    try:
        execute_alignment(front, f'{res_path}/alignment.bin')
    except Exception as exc:
        raise HTTPException(status_code=518, detail="alignment error") from exc
    try:
        execute_parsing(front, f'{res_path}/parsing.png')
    except Exception as exc:
        raise HTTPException(status_code=519, detail="parsing error") from exc

    if front:
        front.save(f'{res_path}/front.png')
    if front_text:
        front_text.save(f'{res_path}/front_text.png')
    if back:
        back.save(f'{res_path}/back.png')
    if back_text:
        back_text.save(f'{res_path}/back_text.png')

    try:
        generate_coin(lib, [
            "",
            f'{res_path}/front.png',
            f'{res_path}/parsing.png',
            f'{res_path}/alignment.bin',
            f'{res_path}/front_text.png' if front_text else f'{settings.KEEPASSET}/WHITE.png',
            f'{coin_path}/coin',
            f'{res_path}/back.png' if back else f'{settings.KEEPASSET}/WHITE.png',
            f'{res_path}/back_text.png' if back_text else f'{settings.KEEPASSET}/WHITE.png',
            border.upper(),
            "MARGIN" if is_pad_front else "NONE",
            "MARGIN" if is_pad_back else "NONE",
            "FACE" if is_face_in_front else "NOFACE",
        ])
    except Exception as exc:
        raise HTTPException(status_code=520, detail=f"generate_coin error, {exc}") from exc


    return {
        "front_image_path": f"/assets/{now}/front.png",
        "back_image_path": f"/assets/{now}/back.png" if back else None,
        # "face_alignment_dst_path": f"/assets/{now}/alignment.bin",
        # "face_parsing_dst_path": f"/assets/{now}/parsing.png",
        "coin_dst_path": {
            # "15_dual" : f"/assets/{now}/coins/coin_15_{border}_dual.stl",
            "15" : f"/assets/{now}/coins/coin_15_{border}.stl",

            # "18_dual" : f"/assets/{now}/coins/coin_18_{border}_dual.stl",
            "18" : f"/assets/{now}/coins/coin_18_{border}.stl",

            # "21_dual" : f"/assets/{now}/coins/coin_21_{border}_dual.stl",
            "21" : f"/assets/{now}/coins/coin_21_{border}.stl",
        },
    }
