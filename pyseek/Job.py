import requests

class Job(dict):

    def __init__(self, jobId, *args, **kwargs):
        self.__dict__ = requests.get(f"https://ca-jobapply-ex-api.cloud.seek.com.au/jobs/{jobId}").json()

    @property
    def basepath(self):
        return f"https://www.seek.com.au/job/{self.id}"

    def url(self, endpoint, ssl=True):
        return f"{self.basepath}/{endpoint.strip('/')}" if endpoint != None else self.basepath
