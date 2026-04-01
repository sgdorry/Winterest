"""
This module provides the glossary query form
"""

import os

import requests

import examples.form_filler as ff

from examples.form_filler import FLD_NM  # for tests

USERNAME = 'username'
PASSWORD = 'password'
COUNTRY = 'country'

API_BASE_URL = os.getenv('WINTEREST_API_BASE_URL', 'http://127.0.0.1:8000')


def fetch_dropdown_choices(endpoint: str,
                           list_key: str,
                           label_key: str = 'name') -> list:
    """
    Fetch dropdown options from an API endpoint.
    Returns [] if the API is unavailable so local form tools still work.
    """
    url = f"{API_BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        payload = resp.json()
        items = payload.get(list_key, [])
        return [item[label_key] for item in items if item.get(label_key)]
    except (requests.RequestException, ValueError, TypeError):
        return []


def fetch_country_choices() -> list:
    return fetch_dropdown_choices('/countries', 'countries', 'name')


def _build_login_form_flds() -> list:
    return [
        {
            FLD_NM: 'Instructions',
            ff.QSTN: 'Enter your username and password.',
            ff.INSTRUCTIONS: True,
        },
        {
            FLD_NM: COUNTRY,
            ff.QSTN: 'Country:',
            ff.PARAM_TYPE: ff.QUERY_STR,
            ff.OPT: True,
            ff.CHOICES: fetch_country_choices(),
        },
        {
            FLD_NM: USERNAME,
            ff.QSTN: 'User name:',
            ff.PARAM_TYPE: ff.QUERY_STR,
            ff.OPT: False,
        },
        {
            FLD_NM: PASSWORD,
            ff.QSTN: 'Password:',
            ff.PARAM_TYPE: ff.QUERY_STR,
            ff.OPT: False,
        },
    ]


def get_form() -> list:
    return _build_login_form_flds()


def get_form_descr() -> dict:
    """
    For Swagger!
    """
    return ff.get_form_descr(get_form())


def get_fld_names() -> list:
    return ff.get_fld_names(get_form())


def main():
    # print(f'Form: {get_form()=}\n\n')
    print(f'Form: {get_form_descr()=}\n\n')
    # print(f'Field names: {get_fld_names()=}\n\n')


if __name__ == "__main__":
    main()
