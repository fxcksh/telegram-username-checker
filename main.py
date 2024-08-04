import argparse
import json
import multiprocessing
import requests
import re
import logging
import coloredlogs

from lxml import html
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

coloredlogs.install(
    level='INFO',
    fmt='%(asctime)s - - %(message)s',
    datefmt='%H:%M:%S',
    logger=logger
)

PREMIUM_USER = 'This account is already subscribed to Telegram Premium.'
CHANNEL = 'Please enter a username assigned to a user.'
NOT_FOUND = 'No Telegram users found.'

class TelegramUsernameChecker(object):

    def __init__(self, file_path, verbose=False):
        self.usernames = set()
        self.session = requests.Session()
        self.file_path = file_path
        self.verbose = verbose

    def load(self):

        logger.debug(f'Loading file: {self.file_path}')

        parsed_url = urlparse(self.file_path)
        # print(parsed_url)
        if parsed_url.netloc != 'raw.githubusercontent.com':
            logger.error(f'URL is not from raw.githubusercontent.com {parsed_url.netloc}')
            return False
        try:
            response = requests.get(self.file_path)
            response.raise_for_status()

            content = response.text.strip()
            if not content:
                logger.error(f'File is empty or contains only whitespace.')
                return False

            self.usernames = set(line for line in content.splitlines() if line.strip())
            logger.debug(f'Usernames loaded: {len(self.usernames)}')
            return True

        except requests.HTTPError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code}")
            return False

        except requests.RequestException as e:
            logger.exception(f"Error fetching usernames: {e}")
            return False

    def check_fragment_api(self, username):

        msg = f' @{username} '

        scripts = html.fromstring(self.session.get('https://fragment.com').content).xpath('//script/text()')

        pattern = re.compile(r'ajInit\((\{.*?})\);', re.DOTALL)

        script = next((script for script in scripts if pattern.search(script)), None)

        if not script:
            msg += f'💔 Init script not found'
            logger.error(msg)
            return False

        api_url = f'https://fragment.com{json.loads(pattern.search(script).group(1)).get("apiUrl")}'

        search_recipient_params = {
            'query': username,
            'months': 3,
            'method': 'searchPremiumGiftRecipient'
        }

        response = self.session.post(api_url, data=search_recipient_params)

        error = response.json().get('error')

        if not error:
            msg += f'👤 User [{response.json().get("found").get("name")}]'
            logger.info(msg)
            return 'User'

        elif CHANNEL in error:

            msg += f'📢 Channel'
            logger.info(msg)
            return f'Channel'

        elif PREMIUM_USER in error:
            msg += f'👑 Premium User [{response.json().get("found").get("name")}]'
            logger.info(msg)
            return 'Premium User'

        elif NOT_FOUND in error:

            search_auctions = {
                'type': 'usernames',
                'query': username,
                'filter': 'sold',
                'method': 'searchAuctions'
            }

            response = self.session.post(api_url, data=search_auctions)

            html_data = json.loads(response.text).get('html')
            pattern = r'@' + re.escape(username)

            match = re.findall(pattern, html_data)
            if match:
                msg += f'💲 Sold'
                logger.info(msg)
                return 'Busy'
            else:
                msg += f'✅ Free'  # TODO False positive results
                logger.warning(msg)
                return 'Free'

    def check(self, username):
        msg = f'@{username} '

        if not re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$').match(username):
            logger.info(msg + '💀 Username not allowed')
            return

        self.check_fragment_api(username)

    def run(self, multithread=True):
        if multithread:
            executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
            executor.map(self.check, self.usernames)
        else:
            [self.check(username) for username in self.usernames]


def parse_args():
    parser = argparse.ArgumentParser(description="Check Telegram usernames.")
    parser.add_argument(
        '--file',
        type=str,
        required=False,
        help='URL to the input file containing usernames'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    return parser.parse_args()


def main():
    args = parse_args()
    checker = TelegramUsernameChecker(file_path=args.file, verbose=args.verbose)
    checker.load()
    checker.run()


if __name__ == "__main__":
    main()
