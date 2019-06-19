import os

from dotenv import load_dotenv

_DOT_ENV_PATH = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(_DOT_ENV_PATH)

from unittest import mock
