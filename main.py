"""
    This scripts sends a user defined number of requests to a URL and calculates avg time of execution.
    If the number is not specified it uses the number of threads availabe on the system.

    Usage: python3 main.py -url <url>
    Run python main.py -h to see all available parameters.
"""

__maintainer__ = "BorysNie"
__date__ = "30/09/2021"

import argparse
import logging
import logging.config
import os
import random
import requests

from multiprocessing import Process
from string import ascii_lowercase, ascii_uppercase, digits
from urllib.parse import urlparse
from time import time

logging.config.fileConfig("log.ini")
log = logging.getLogger(__name__)

def web_request(url: str, params: dict) -> None:
    """ This function attempts to send requests to the URL with parameters provided """
    try:
        log.info(f"Sending request to {url}, params {params}")
        requests.get(url=url, params=params)
    except Exception as exc:
        log.error(exc)


def validate_url(url: str) -> bool:
    """ This function validates the format of the provided URL """
    try:
        parsed_url = urlparse(url)
        if all([parsed_url.scheme, parsed_url.netloc]):
            result = True
    except ValueError:
        result = False
    return result

def cli_args() -> any:
    """ This function parses all command line arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", dest="url", type=str, action="store", default="", required=True,
        help="Url to which send the requests to, requires http|https://")
    parser.add_argument("-threads", dest="threads", type=int, action="store", default=os.cpu_count(),
        help="Defaults to use the available logical processors/threads on the system.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-params", dest="params", type=str, action="store", default="",
        help="""
        CLI takes string, requests params uses dict, tuple or bytes in query string to send
        eg python3 ./main.py -u URL -params {"foo":"bar"} | "(foo, bar)"
        """)
    group.add_argument("-random", dest="random", action="store_true", default=False,
        help="Randomly generates and appends to the URL ?ref=#, modified under k=8")
    return vars(parser.parse_args())

def main(args: any) -> None:
    """ This function sets up and runs the number of requests to be processed parallelly """
    log.info(f"Parent process id: {os.getpid()}")
    log.info(f"Starting with parameters: {args}")

    url = args['url']
    params = args['params']
    processes = []
    start_times = []
    end_times = []
    total_times = []

    if validate_url(url):
        for thread in range(args['threads']):
            log.info(f"Registering process {thread}")

            # If random is true, ?ref=<random> will be appended to the end of the URL.
            if args['random']:
                params = {"ref": "".join(random.choices(
                    ascii_lowercase + ascii_uppercase + digits, k=8))}

            processes.append(Process(target=web_request, args=(url, params,)))

        for process in processes:
            log.info(f"Starting process: {process}")
            process.start()
            start_times.append(time())

        for process in processes:
            log.info(f"Joining process: {process}")
            process.join()
            end_times.append(time())

        for start in start_times:
            for end in end_times:
                total_times.append(end - start)

        delta = round(sum(total_times) / len(total_times), 2)

        log.info(f"Time Delta: {delta} seconds")
    else:
        log.error("Invalid URL")

if __name__ == "__main__":
    args = cli_args()
    main(args)
