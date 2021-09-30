"""
    This scripts sends a user defined number of requests to a URL and calculates avg time of execution.
    If the number is not specified it uses the number of threads availabe on the system.

    Usage: python3 main.py -url <url>
    Run python main.py -h to see all available parameters.
"""

__maintainer__ = 'Borys Niedbala'
__date__ = '30/09/2021'

import argparse
import logging
import logging.config
import os
import random
import requests

from multiprocessing import Process
from string import ascii_lowercase, digits
from urllib.parse import urlparse
from time import time

logging.config.fileConfig('log.ini')
log = logging.getLogger(__name__)

def web_request(url: str, params: dict):
    """ This function attempts to send requests to the URL with parameters provided """
    try:
        log.info(f'Sending request to {url} with parameters {params}')
        log.info(requests.get(url, params=params))
    except Exception as e:
        log.error(e)

def validate_url(url: str) -> bool:
    """ This function validates the format of the provided URL """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def cli_args():
    """ This function parses all command line arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('-url', dest='url', type=str, action='store', default='', required=True)
    parser.add_argument('-params', dest='params',type=str, action='store', default={})
    parser.add_argument('-random', dest='random', action='store_true', default=False)
    parser.add_argument('-threads', dest='threads',type=int, action='store', default=os.cpu_count())
    return vars(parser.parse_args())

def main(args):
    """ This function sets up and runs the number of requests to be processed parallelly """
    log.info(f'Parent process Pid: {os.getpid()}')
    log.info(f'Starting with parameters: {args}')

    url = args['url']
    params = args['params']
    processes = []
    start_times = []
    end_times = []
    total_times = []

    if validate_url(url):
        for thread in range(args['threads']):
            log.info(f'Registering process {thread}')

            # If random is true, ?ref=<random> will be appended to the end of the URL.
            if args['random']:
                params = {'ref': ''.join(random.choices(ascii_lowercase + digits, k=8))}

            processes.append(Process(target=web_request, args=(url, params,)))

        for process in processes:
            log.info(f'Starting process: {process}')
            start_times.append(time())
            process.start()

        for process in processes:
            log.info(f'Joining process: {process}')
            process.join()
            end_times.append(time())

        for start in start_times:
            for end in end_times:
                total_times.append(end - start)

        delta = round(sum(total_times) / len(total_times), 2)

        log.info(f'Time Delta: {delta} seconds')
    else:
        log.error('Invalid URL')

if __name__ == '__main__':
    args = cli_args()
    main(args)
