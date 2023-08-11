import configparser
from pathlib import Path

from mongoengine import connect


config_path: Path = Path(__file__).parent.joinpath("config_add.ini")
config = configparser.ConfigParser()
config.read(config_path)

username: str = config.get('DB', 'username')
password: str = config.get('DB', 'password')
db_name: str = config.get('DB', 'db_name')
domain: str = config.get('DB', 'domain')

url: str = f"mongodb+srv://{username}:{password}@{domain}/{db_name}"

try:
    con = connect(host=url, ssl=True)
except Exception as err:
    print(err)
