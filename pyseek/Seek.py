import functools
import json
import logging
import requests
import yaml

from Job import Job
from utils import clean_host_str, get_yaml_config

class SeekListings():

    def __init__(self, config="./config/seek.yml", creds="./config/credentials.yml"):
        self.log = logging.getLogger("seekListings")
        self._logged_in = False

        self.__dict__.update(get_yaml_config(config))
        if creds != None:
            self.__dict__.update(get_yaml_config(creds))

    def url(self, endpoint, ssl=True):
        return f"https://{self.host}/{endpoint.strip('/')}"

    def authorised(func):

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):

            with requests.Session() as sesh:

                sesh.headers.update(self.headers)

                if not(self._logged_in):
                    login_resp = sesh.post(self.url("/userapi/login"),
                        json={
                            "rememberMe": True,
                            "email": self.username,
                            "password": self.password
                        }
                    )

                    if not(login_resp.ok):
                        self.log.error(f"Failed to login with credentials for {self.username}")
                        login_resp.raise_for_status()
                    else:
                        self.log.info("Logged in")
                        self._logged_in = True

                token_resp = sesh.get(self.url("/apitoken/getAuthorisationToken"))
                if not(token_resp.ok):
                    self.log.error("Failed to get API token")
                    token_resp.raise_for_status()

                token = token_resp.json()
                sesh.headers.update({"authorization": f'Bearer {token["access_token"]}'})
                r = func(self, sesh, *args, **kwargs)

            return r
        return wrapper

    @authorised
    def post_graphql(self, session, operation, **kwargs):

        if operation not in self.graphql:
            return False # TODO: error handling

        if "variables" in self.graphql[operation]:
            for k,v in self.graphql[operation]["variables"].items():
                if k not in kwargs and "default" not in v:
                    return False # TODO: error handling, missing variable
                elif k not in kwargs:
                    kwargs[k] = v["default"]

        post_body = {
            'operationName': operation,
            'query': self.graphql[operation]["query"],
            'variables': kwargs
        }
        prepped = session.prepare_request(
            requests.Request("POST", self.url("/graphql"),
                json=post_body
            )
        )
        resp = session.send(prepped)
        return resp

    def get_jobs(self, keywords="", where="", page=1, last_page=None):

        self.log.info(f"GET api/chalice-search/search with keywords={keywords}; where={where}; page={page}")
        resp = requests.get(self.url("api/chalice-search/search"),
                            params={"keywords":keywords,
                                    "where":where,
                                    "page":page}
                            )
        self.log.debug(f"{resp.status_code} {resp.reason}")
        jobs = [Job(x["id"]) for x in resp.json()["data"]]

        if last_page is not None:
            while page < last_page:
                page += 1
                jobs.extend(self.get_jobs(keywords=keywords, where=where, page=page, last_page=last_page))

        return jobs
