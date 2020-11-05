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


def get_generic(source, url, qs={}):
    with metrics.http_request_timer(source) as timer:
        query_string = build_query_string({"count_total": "true", **qs})
        url = (
            base_url
            + url
            + (
                # can only filter from the /search endpoint
                ""
                if "updated_after_utc" not in qs or qs.get('updated_after_utc') is None
                else "/Search"
            )
            + query_string
        )
        resp = session.request(method="get", url=url)

        if resp.status_code == 401:
            raise AuthException(resp.text)
        if resp.status_code == 403:
            raise AuthException(resp.text)
        if resp.status_code == 404:
            raise NotFoundException(resp.text)
        resp.raise_for_status()  # throw exception if not 200

        timer.tags[metrics.Tag.http_status_code] = resp.status_code
        return resp.json(), resp


def get_all_pages(source, url, extra_query_string={}):
    skip = 0

    while True:
        json, resp = get_generic(
            source, url, {**extra_query_string, "skip": skip, "top": pageSize},
        )
        yield json
        skip += pageSize
        total = resp.headers.get("x-total-count")
        if total == None or skip > int(total):
            break


def get_endpoint(resource):
    endpoints = {"pipeline_stages": "PipelineStages"}
    # get endpoint if available, default to just resource name
    return endpoints.get(resource, resource)


def formatDate(dt):
    return datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def build_query_string(dict):
    if len(dict) == 0:
        return ""

    return "?" + "&".join(["{}={}".format(k, v) for k, v in dict.items()])
