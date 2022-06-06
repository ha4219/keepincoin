'''
settings
'''
from pydantic import BaseSettings


class Settings(BaseSettings):
    '''
    init setting
    '''
    KEEPMODEL: str = "/keepincoin/models"
    KEEPASSET: str = "/keepincoin/assets"
    KEEPCUDA: str = "cpu"

    class Config:
        '''
        read .env
        '''
        env_file = ".env"
