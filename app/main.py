"""
main fastapi
"""
import os
import platform
import io
import ctypes
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch
import numpy as np
from PIL import Image

from app.config import Settings
from app.face_parsing.face_parsing import _execute_face_parsing
from app.coin_generator.generator import generate_coin
from app.path_util import now_to_str

settings = Settings()

app = FastAPI()

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
    return {"version": "0.0.34"}



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
    """
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
        "front_image_path": 앞면 이미지 파일 위치,
        "back_image_path": 뒷면 이미지 파일 위치 없을 경우 null,
        "coin_dst_path": { coin 위치 path, naming_rule: size_options..., 아래는 예시입니다.
            "12_dual_margin" : f"/assets/{now}/coins/coin_12_dual_margin.stl",
            "12_dual" : f"/assets/{now}/coins/coin_12_dual.stl",
            "12_margin" : f"/assets/{now}/coins/coin_12_margin.stl",
            "12" : f"/assets/{now}/coins/coin_12.stl",

            "15_dual_margin" : f"/assets/{now}/coins/coin_15_dual_margin.stl",
            "15_dual" : f"/assets/{now}/coins/coin_15_dual.stl",
            "15_margin" : f"/assets/{now}/coins/coin_15_margin.stl",
            "15" : f"/assets/{now}/coins/coin_15.stl",

            "18_dual_margin" : f"/assets/{now}/coins/coin_18_dual_margin.stl",
            "18_dual" : f"/assets/{now}/coins/coin_18_dual.stl",
            "18_margin" : f"/assets/{now}/coins/coin_18_margin.stl",
            "18" : f"/assets/{now}/coins/coin_18.stl",

            "21_dual_margin" : f"/assets/{now}/coins/coin_21_dual_margin.stl",
            "21_dual" : f"/assets/{now}/coins/coin_21_dual.stl",
            "21_margin" : f"/assets/{now}/coins/coin_21_margin.stl",
            "21" : f"/assets/{now}/coins/coin_21.stl",

            "24_dual_margin" : f"/assets/{now}/coins/coin_24_dual_margin.stl",
            "24_dual" : f"/assets/{now}/coins/coin_24_dual.stl",
            "24_margin" : f"/assets/{now}/coins/coin_24_margin.stl",
            "24" : f"/assets/{now}/coins/coin_24.stl",
        }
    """
    if not front:
        raise HTTPException(status_code=517, detail="front parameter is required.")
    front = Image.open(io.BytesIO(await front.read())).convert('RGB').resize((512, 512))
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
        ])
    except Exception as exc:
        raise HTTPException(status_code=520, detail=f"generate_coin error, {exc}") from exc


    return {
        "front_image_path": f"/assets/{now}/front.png",
        "back_image_path": f"/assets/{now}/back.png" if back else None,
        "face_alignment_dst_path": f"/assets/{now}/alignment.bin",
        "face_parsing_dst_path": f"/assets/{now}/parsing.png",
        "coin_dst_path": {
            "12_dual_margin" : f"/assets/{now}/coins/coin_12_dual_margin.stl",
            "12_dual" : f"/assets/{now}/coins/coin_12_dual.stl",
            "12_margin" : f"/assets/{now}/coins/coin_12_margin.stl",
            "12" : f"/assets/{now}/coins/coin_12.stl",

            "15_dual_margin" : f"/assets/{now}/coins/coin_15_dual_margin.stl",
            "15_dual" : f"/assets/{now}/coins/coin_15_dual.stl",
            "15_margin" : f"/assets/{now}/coins/coin_15_margin.stl",
            "15" : f"/assets/{now}/coins/coin_15.stl",

            "18_dual_margin" : f"/assets/{now}/coins/coin_18_dual_margin.stl",
            "18_dual" : f"/assets/{now}/coins/coin_18_dual.stl",
            "18_margin" : f"/assets/{now}/coins/coin_18_margin.stl",
            "18" : f"/assets/{now}/coins/coin_18.stl",

            "21_dual_margin" : f"/assets/{now}/coins/coin_21_dual_margin.stl",
            "21_dual" : f"/assets/{now}/coins/coin_21_dual.stl",
            "21_margin" : f"/assets/{now}/coins/coin_21_margin.stl",
            "21" : f"/assets/{now}/coins/coin_21.stl",

            "24_dual_margin" : f"/assets/{now}/coins/coin_24_dual_margin.stl",
            "24_dual" : f"/assets/{now}/coins/coin_24_dual.stl",
            "24_margin" : f"/assets/{now}/coins/coin_24_margin.stl",
            "24" : f"/assets/{now}/coins/coin_24.stl",
        },
        "style": style,
        "shape": shape,
        "border": border,
        "embo": embo,
        "emboline": emboline,
    }
