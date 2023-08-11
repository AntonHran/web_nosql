import json
import timeit
import re
from pprint import pprint

import redis

from models_ import Quote
from connection_ import conn


client = redis.StrictRedis(
    host="localhost", port=6379, username="default", password=None, db=1
)


def find_quotes_by_name(name: str) -> dict[str]:
    result: dict = {}
    for quote_ in Quote.objects():
        if re.match(pattern=name, string=quote_.author.full_name, flags=re.I):
            if quote_.author.full_name not in result.keys():
                result.update({quote_.author.full_name: [quote_.quote]})
            else:
                result[quote_.author.full_name].append(
                    quote_.quote
                    if quote_.quote not in result[quote_.author.full_name]
                    else None
                )
    return result


def find_quotes_by_tag(tag_: str) -> dict[str]:
    result: dict = {}
    for quote_ in Quote.objects():
        tags = []
        for qu_tag in quote_.tags:
            for tag in tag_.split(","):
                if re.match(pattern=tag, string=qu_tag, flags=re.I):
                    tags.append(qu_tag)
        if tags:
            result.update({tuple(tags): quote_.quote})
    return result


def search_in_keys(key: str) -> list:
    keys: list[str] = [
        key_.decode()
        for key_ in client.scan()[1]
        if re.match(pattern=key, string=key_.decode(), flags=re.I)
    ]
    return keys


def get_from_cache_by_name(name: str) -> list:
    name_key: list = search_in_keys(name)
    if name_key:
        return [client.get(name_).decode() for name_ in name_key]


def get_from_cache_by_tag(tag) -> list | None:
    result: list[str] = []
    for tag_ in tag.split(","):
        tag_key = search_in_keys(tag_)
        if tag_key:
            [
                result.append(client.get(tag_k).decode())
                for tag_k in tag_key
                if client.get(tag_k).decode() not in result
            ]
        return None
    return result


def get_quotes_by_name_cache(name) -> list | str:
    result_cache = get_from_cache_by_name(name)
    if result_cache:
        return result_cache
    result_db = find_quotes_by_name(name)
    for author_name, quote in result_db.items():
        client.set(author_name, json.dumps(quote), ex=300)
    return list(result_db.values())


def get_quotes_by_tag_cache(tag) -> str | list:
    result_cache = get_from_cache_by_tag(tag)
    if result_cache:
        return result_cache
    result_db = find_quotes_by_tag(tag)
    for tag_keys, quote in result_db.items():
        [client.set(tag_key, quote, ex=300) for tag_key in tag_keys]
    return list(result_db.values())


function = {
    "name": get_quotes_by_name_cache,
    "tag": get_quotes_by_tag_cache,
}


def parser(text: str) -> tuple:
    try:
        parameter, value = text.split(": ")
        if parameter in function:
            return function[parameter], value
        else:
            print(f"There are not a such command: {parameter}")
    except ValueError as err:
        print(err)


def handler(parsed_val: tuple):
    try:
        func, values = parsed_val
        return func(values)
    except (ValueError, TypeError) as err:
        print(err)


def find_by():
    while True:
        text: str = input("\nEnter key and its value for searching: ")
        if text == "exit":
            break
        # start = timeit.default_timer()
        result = handler(parser(text))
        # print(timeit.default_timer() - start)
        if result:
            pprint(result)
        else:
            print("Nothing was found...")


if __name__ == "__main__":
    find_by()


"""
def get_quotes_by_name_cache(name):
    result = []
    name_key = search_in_keys(name)
    if client.get(name_key):
        result.append(client.get(name).decode())
    else:
        for quote_ in Quote.objects():
            if re.match(pattern=name, string=quote_.author.full_name, flags=re.I):
                result.append(quote_.quote) if quote_.quote not in result else None

        client.set(name_key, json.dumps(result), ex=300)

    return result

# b = [quote_.quote for tag in tag_.split(',') for quote_ in Quote.objects() if tag in quote_.tags]
def get_quotes_by_tag_cache(tag_):
    result: list[str] = []
    for tag in tag_.split(','):
        tag_key = search_in_keys(tag)
        if client.get(tag_key):
            result.append(client.get(tag_key).decode())
        else:
            for quote_ in Quote.objects():
                for qu_tag in quote_.tags:
                    if re.match(pattern=tag, string=qu_tag, flags=re.I):
                        result.append(quote_.quote) if quote_.quote not in result else None
                        client.rpush(qu_tag, *[quote_.quote]) if quote_.quote not in client.get(qu_tag) else None
    return result
    
function = {'name': find_quotes_by_name,
            'tag': find_quotes_by_tag, }
            
"""
