'''app settings'''
from app.core.settings.base import BaseAppSettings
from platform import platform


# @TODO(ha4219):FEAT #12 set config file
class AppSettings(BaseAppSettings):
    '''
        app settings
    '''
    os: str

    def __init__(self):
        print(self.KEEPMODEL)
