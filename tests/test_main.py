'''
    test main.py
'''
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_read_main():
    '''
        test read main
    '''
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_upoloader_front_not():
    '''
        test uploader
    '''
    response = client.post('/uploader')
    assert  response.status_code == 517

def test_uploader_405():
    '''
        test get uploader
    '''
    response = client.get('/uploader')
    assert response.status_code == 405

def test_uploader_front_no_face():
    '''
        test uploader no face
    '''
    response = client.post(
        '/uploader',
        files={"front": ("assets/BLACK.png", open('assets/BLACK.png', 'rb'), "image/jpeg")}
    )
    assert response.status_code == 518

def test_uploader_front_success():
    '''
        test uploader no face
    '''
    response = client.post(
        '/uploader',
        files={"front": ("assets/test.png", open('assets/test.png', 'rb'), "image/jpeg")}
    )
    assert response.status_code == 200 