import logging
import os
import requests_cache

requests_cache.install_cache('testing.cache')

from Seek import SeekListings
from utils import get_logging_dictconfig

get_logging_dictconfig(clear_log=True)

def example_getJobList():

    seek = SeekListings()

    for job in seek.get_jobs(keywords="engineering", where="Perth", last_page=2):
        if not(job.isLinkOut):
            print(f"{job.basepath:40}{job.advertiser['description']:50}{job.title:80}({job.workType['description']})")


def example_graphQL():

    seek = SeekListings()

    r = seek.post_graphql("GetJobDetails", regionalId=51724832)
    print(r.json())

    r = seek.post_graphql("GetProfile")
    print(r.json())

if __name__ == '__main__':
    example_getJobList()