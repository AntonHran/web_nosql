from pathlib import Path
from datetime import datetime
from pprint import pprint

from models_ import Author, Quote
from connection_ import conn
from validation import validation, validate


author_path = Path('async_authors.json')
quotes_path = Path('async_quotes.json')


@validation
def seed_authors(authors_data: list[dict]) -> list[Author]:
    res: list[Author] = []
    for author_record in authors_data:
        author = Author(full_name=author_record['full_name'],
                        born_date=datetime.strptime(
                            author_record['born_date'].replace(',', ''), '%B %d %Y').date(),
                        born_location=author_record['born_location'],
                        description=author_record['description']).save()
        res.append(author)
    return res


@validation
def seed_quotes(quotes_data: list[dict], authors: list[Author]) -> None:
    for quote_record in quotes_data:
        for author in authors:
            if author.full_name == quote_record["author"]:
                Quote(tags=quote_record["tags"],
                      author=author,
                      quote=quote_record["quote"]).save()


def seed_main() -> None:
    data_authors = validate(author_path, Author)
    auth = []
    if data_authors:
        auth = seed_authors(data_authors)
    else:
        print('Do not write the same authors!')
    data_quotes = validate(quotes_path, Quote)
    # pprint(data_quotes)
    if data_quotes and auth:
        seed_quotes(data_quotes, auth)
    elif data_quotes and not auth:
        authors = Author.objects()
        seed_quotes(data_quotes, authors)
    else:
        print('Do not write the same quotes!')


if __name__ == '__main__':
    seed_main()
