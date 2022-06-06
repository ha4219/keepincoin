'''app settings'''
from app.core.settings.base import BaseAppSettings
from platform import platform


class AppSettings(BaseAppSettings):
    '''
        app settings
    '''
    os: str

    def __init__(self):
        print(self.KEEPMODEL)
