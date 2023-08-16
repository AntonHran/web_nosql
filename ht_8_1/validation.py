import json
from pathlib import Path
from functools import wraps

from models_ import Document
from connection_ import conn


class ValidationException(Exception):
    def __init__(self, message='Value can not be missing/empty.') -> None:
        self.message = message
        super().__init__(self.message)


def validation(func):
    @wraps(func)
    def wrapper(*args):
        for el in args:
            if el is None:
                raise ValidationException()
        result = func(*args)
        return result
    return wrapper


def get_data(path_file: Path) -> list[dict]:
    try:
        with open(path_file, encoding='utf-8') as fr:
            file_data: list[dict] = json.load(fr)
        return file_data
    except EOFError as error:
        print(error)


def check_repeats(data: list[dict], obj: Document) -> list[dict]:
    result: list[dict] = []
    records_db: list = obj.objects()
    for record_db in records_db:
        for record_file in data:
            for key_file in record_file:
                attr = find_attribute(obj, key_file)
                if attr and record_file[key_file] == getattr(record_db, attr):
                    result.append(record_file)
                    break
    return result


def find_attribute(obj: Document, key_file: str) -> str:
    if key_file in vars(obj).keys():
        return key_file


def cut_file(fragment: list, data: list) -> list[dict]:
    for rec in fragment:
        try:
            data.remove(rec)
        except ValueError as err:
            print(err)
    return data


def validate(path: Path, obj) -> list[dict]:
    data: list[dict] = get_data(path)
    fr: list[dict] = check_repeats(data, obj)
    if fr:
        return cut_file(fr, data)
    return data
