import os
import requests
import singer.metrics as metrics
from datetime import datetime


session = requests.Session()


class AuthException(Exception):
    pass


class NotFoundException(Exception):
    pass


# constants
base_url = "https://api.insightly.com/v3.1/"
pageSize = 500




def get_endpoint(resource):
    endpoints = {"pipeline_stages": "PipelineStages"}
    # get endpoint if available, default to just resource name
    return endpoints.get(resource, resource)


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def build_query_string(dict):
    if len(dict) == 0:
        return ""

    return "?" + "&".join(["{}={}".format(k, v) for k, v in dict.items()])
