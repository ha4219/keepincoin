"""
    test main.py
"""
from itertools import product
from typing import List

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

front_names: List[str] = ["assets/test.png"]
front_text_names = [None, "BLACK.png", "WHITE.png"]
back_names = ["assets/test.png"]
back_text_names = [None, "BLACK.png", "WHITE.png"]
styles = ["charm", "frame"]
shapes = ["circle", "square", "eplipse", "octagon"]
borders = ["basic", "baed", "twist", "curve"]
emboes = [True, False]
embolines = [True, False]

def test_read_main():
    """
        test read main
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_upoloader_front_not():
    """
        test uploader
    """
    response = client.post('/uploader')
    assert  response.status_code == 517

def test_uploader_405():
    """
        test get uploader
    """
    response = client.get('/uploader')
    assert response.status_code == 405

def test_uploader_front_no_face():
    """
        test uploader no face
    """
    with open('assets/BLACK.png', 'rb') as image:
        response = client.post(
            '/uploader',
            files={"front": ("assets/BLACK.png", image, "image/jpeg")}
        )
        assert response.status_code == 518

def test_uploader_only_front_success():
    """
        test uploader success
    """
    with open('assets/test.png', 'rb') as image:
        response = client.post(
            '/uploader',
            files={"front": ("assets/test.png", image, "image/jpeg")}
        )
        assert response.status_code == 200

def test_uploader_combination_success():
    """
        test uploader all combination
    """
    for (
        front_name,
        front_text_name,
        back_name,
        back_text_name,
        style,
        shape,
        border,
        embo,
        emboline,
    ) in product(
        front_names,
        front_text_names,
        back_names,
        back_text_names,
        styles,
        shapes,
        borders,
        emboes,
        embolines,
    ):
        with open(front_name, 'rb') as front, \
            open(front_text_name, 'rb') as front_text, \
            open(back_name, 'rb') as back, \
            open(back_text_name, 'rb') as back_text:
            response = client.post(
                "/uploader",
                files={
                    "front": (
                        front_name, front, "image/jpeg",
                    ),
                    "text": (
                        front_text_name, front_text, "image/jpeg",
                    ),
                    "back": (
                        back_name, back, "image/jpeg",
                    ),
                    "back_text": (
                        back_text_name, back_text, "image/jpeg",
                    ),
                    "style": style,
                    "shape": shape,
                    "border": border,
                    "embo": embo,
                    "emboline": emboline
                }
            )
            assert response.status_code == 200
