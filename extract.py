'''
	extract model shape and weights
'''
import os
import torch

from app.config import Settings
from app.face_parsing import BiSeNet
from app import face_alignment


def extract_model_feature():
    '''
		function
		:parameter {None}: none
		:return {None}: none
	'''
    settings = Settings()
    alignment = face_alignment.FaceAlignment(face_alignment.LandmarksType._3D, flip_input=False)

    torch.save(alignment, os.path.join(settings.KEEPMODEL, "face_alignment.pth"))

    weight_path = "app/face_parsing/res/cp/79999_iter.pth"
    parsing = BiSeNet(19)
    parsing.load_state_dict(torch.load(weight_path, map_location='cpu'))

    torch.save(parsing, os.path.join(settings.KEEPMODEL, 'face_parsing.pth'))


if __name__ == '__main__':
    extract_model_feature()
