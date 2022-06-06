'''
	extract model shape and weights
'''
import os
import torch
from config import Settings

from face_parsing import BiSeNet
from face_alignment import FaceAlignment


def extract_model_feature():
    '''
		function
		:parameter {None}: none
		:return {None}: none
	'''
    settings = Settings()
    alignment = FaceAlignment(3, flip_input=False)

    torch.save(alignment, os.path.join(settings.KEEPMODEL, "face_alignment.pth"))

    weight_path = "face_parsing/res/cp/79999_iter.pth"
    parsing = BiSeNet(19)
    parsing.load_state_dict(torch.load(weight_path, map_location='cpu'))

    torch.save(parsing, os.path.join(settings.KEEPMODEL, 'face_parsing.pth'))


if __name__ == '__main__':
    extract_model_feature()
