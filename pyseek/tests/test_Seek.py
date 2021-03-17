import os
import pytest
import requests
import requests_cache
from unittest.mock import MagicMock, patch
import yaml

from Seek import SeekListings

requests_cache.install_cache('testing.cache')

@pytest.fixture
def SeekListingsDefault():
    return SeekListings("./config/seek.yml")

@pytest.fixture
def SeekListingsWithCreds(tmp_path):

    creds = {"username": "SomeUser@gmail.com", "password": "Password1234!@#$"}
    creds_file = os.path.join(tmp_path, "creds.yml")
    with open(creds_file, 'w') as fd:
        yaml.dump(creds, fd)

    return SeekListings("./config/seek.yml", creds=creds_file)

@pytest.fixture
def authorised_session(requests_mock):
    requests_mock.post("https://www.seek.com.au/userapi/login")

    requests_mock.get("https://www.seek.com.au/apitoken/getAuthorisationToken",
        json={"access_token": "some_token"}
    )

    cj = requests.cookies.RequestsCookieJar()
    cj.update({
            "Login": "LoginCookie1234abcdefghijkl123_123",
            ".ASPXAUTH": "abcdefghijklmnopqrstuvwxyz"
        }
    )
    with patch('requests.Session', new=MagicMock(wraps=requests.Session)) as mock:
        session_instance = mock.return_value.__enter__.return_value
        session_instance.headers = {'authorization': 'Bearer token'}
        session_instance.cookies = cj
        yield session_instance

def test_Seek_configLoad(SeekListingsDefault):

    assert SeekListingsDefault.host == "www.seek.com.au"
    assert isinstance(SeekListingsDefault.headers, dict)
    assert SeekListingsDefault.headers["authority"] == "www.seek.com.au"
    assert SeekListingsDefault.headers["accept"] == "application/json, text/plain, */*"
    assert SeekListingsDefault.headers["sec-ch-ua"] == '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"'

def test_Seek_configLoad_withCredentials(SeekListingsWithCreds):

    assert SeekListingsWithCreds.username == "SomeUser@gmail.com"
    assert SeekListingsWithCreds.password == "Password1234!@#$"

def test_Seek_authorised(SeekListingsWithCreds, authorised_session):

    @SeekListings.authorised
    def test(SeekListingsWithCreds, session):
        assert session.cookies["Login"] == "LoginCookie1234abcdefghijkl123_123"
        assert session.cookies[".ASPXAUTH"] == "abcdefghijklmnopqrstuvwxyz"
        assert session.headers["authorization"] == "Bearer token"

    with authorised_session:
        test(SeekListingsWithCreds)

