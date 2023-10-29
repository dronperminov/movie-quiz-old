import hashlib
import os
import shutil
from datetime import datetime
from typing import List

import cv2
from fastapi import UploadFile

from src import constants


def get_default_question_years() -> List[List[int]]:
    years = []

    for i, year in enumerate(constants.QUESTION_YEARS[1:]):
        years.append([constants.QUESTION_YEARS[i], year - 1])

    years.append([constants.QUESTION_YEARS[-1], datetime.now().year])
    return years


def get_word_form(questions: int, word_forms: List[str]) -> str:
    if questions % 10 in {0, 5, 6, 7, 8, 9} or questions in {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}:
        return word_forms[0]

    if questions % 10 in {2, 3, 4}:
        return word_forms[1]

    return word_forms[2]


def crop_image(path: str) -> None:
    image = cv2.imread(path)
    height, width = image.shape[:2]
    size = min(height, width)
    x, y = (width - size) // 2, (height - size) // 2
    image = image[y:y + size, x:x + size]
    image = cv2.resize(image, (constants.CROP_IMAGE_SIZE, constants.CROP_IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, image)


def save_image(image: UploadFile, output_dir: str) -> str:
    file_name = image.filename.split("/")[-1]
    file_path = os.path.join(output_dir, file_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    finally:
        image.file.close()

    crop_image(file_path)
    return file_path


def get_hash(filename: str) -> str:
    hash_md5 = hashlib.md5()

    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()
