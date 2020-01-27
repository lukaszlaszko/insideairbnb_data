import gzip
import os
import requests
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from fnmatch import fnmatch
from http import HTTPStatus
from loguru import logger
from urllib.parse import urlparse
from tqdm import tqdm


@logger.catch()
def main(args):
    logger.info(f'loading {args.url}')

    response = requests.get(args.url)
    if response.status_code != HTTPStatus.OK:
        logger.error(f'{args.url} http code {response.status_code}')
        return os.EX_UNAVAILABLE

    logger.info('loading links')
    soup = BeautifulSoup(response.text, features="html.parser")
    for a in soup.findAll('a'):
        if 'href' in a.attrs:
            href = a['href']
            compressed = False

            if 'visualisations' in href:
                continue

            noext, ext = os.path.splitext(href)
            if ext == '.gz':
                compressed = True
                _, ext = os.path.splitext(noext)

            if ext == '.csv':
                url = urlparse(href)
                urlpath = os.path.relpath(url.path, '/')
                if args.filters and any(filter not in urlpath.lower() for filter in args.filters):
                    continue

                filepath = os.path.join(args.workdir, urlpath)
                if os.path.exists(filepath) and not args.force:
                    continue

                with tqdm(desc=f' downloading {href}', unit='b', unit_scale=True) as progress:
                    response = requests.get(href, stream=True)
                    if response.status_code != HTTPStatus.OK:
                        logger.warning(f'cannot download {href} status {response.status_code}')
                        continue

                    progress.total = int(response.headers['content-length'])

                    filedir, _ = os.path.split(filepath)
                    os.makedirs(filedir, exist_ok=True)

                    if compressed:
                        with open(filepath, 'wb') as f:
                            for chunk in response:
                                progress.update(len(chunk))
                                f.write(chunk)
                    else:
                        with gzip.open(filepath + '.gz', 'wb') as f:
                            for chunk in response:
                                f.write(chunk)

    return os.EX_OK


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--url', default='http://insideairbnb.com/get-the-data.html')
    parser.add_argument('--workdir', default='.')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--filters', nargs='+', default=None)

    args = parser.parse_args()
    exit(main(args))
