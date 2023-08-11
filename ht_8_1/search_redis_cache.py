import timeit
import re

import redis
from redis_lru import RedisLRU

from models_ import Quote
from connection_ import conn


client = redis.StrictRedis(host="localhost",
                           port=6379,
                           username='default',
                           password=None,
                           db=0)
cache = RedisLRU(client)


@cache
def find_quotes_by_name(name: str) -> list:
    result = []
    for quote_ in Quote.objects():
        if re.match(pattern=name, string=quote_.author.full_name, flags=re.I):
            result.append(quote_.quote)
    return result


@cache
def find_quotes_by_tag(tag_: str) -> list:
    result = []
    for quote_ in Quote.objects():
        for qu_tag in quote_.tags:
            for tag in tag_.split(','):
                if re.match(pattern=tag, string=qu_tag, flags=re.I):
                    result.append(quote_.quote)
    return result


def find_by():
    while True:
        result = ''
        text: str = input('\nEnter key and its value for finding: ')
        if text == 'exit':
            break
        elif text.startswith('name'):
            _, value = text.split(': ')
            # start = timeit.default_timer()
            result = find_quotes_by_name(value)
            # print(timeit.default_timer() - start)
        elif text.startswith('tag'):
            _, value = text.split(': ')
            # start = timeit.default_timer()
            result = find_quotes_by_tag(value)
            # print(timeit.default_timer() - start)
        if result:
            for r in result:
                print(r)
        else:
            print('Nothing was found...')


if __name__ == '__main__':
    find_by()
