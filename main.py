import argparse
import json
import logging
import multiprocessing
import re
import time
import coloredlogs
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from lxml import html
from config import RESERVED_WORDS


logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', fmt='%(message)s', logger=logger)

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
        if parsed_url.netloc != 'raw.githubusercontent.com':
            logger.error(f'URL is not from raw.githubusercontent.com {parsed_url.netloc}')
            return
        try:
            response = requests.get(self.file_path)
            response.raise_for_status()
            content = response.text.strip()
            if not content:
                logger.error(f'File is empty or contains only whitespace.')
                return
            self.usernames = set(line for line in content.splitlines() if line.strip())
            logger.debug(f'Usernames loaded: {len(self.usernames)}')
            return True
        except requests.HTTPError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code}")
            return
        except requests.RequestException as e:
            logger.exception(f"Error fetching usernames: {e}")
            return

    def get_api_url(self):
        scripts = html.fromstring(self.session.get('https://fragment.com').content).xpath('//script/text()')
        pattern = re.compile(r'ajInit\((\{.*?})\);', re.DOTALL)
        script = next((script for script in scripts if pattern.search(script)), None)
        if script:
            api_url = f'https://fragment.com{json.loads(pattern.search(script).group(1)).get("apiUrl")}'
            return api_url

    def get_user(self, username, api_url):
        search_recipient_params = {'query': username, 'months': 3, 'method': 'searchPremiumGiftRecipient'}
        response = self.session.post(api_url, data=search_recipient_params)
        error = response.json().get('error')
        return error

    def get_telegram_web_user(self, username):
        response = self.session.get(f'https://t.me/{username}')
        text = f"You can contact @{username} right away."
        return text in html.fromstring(response.content)

    def check_fragment_api(self, username, count=6):
        if count == 0:
            return
        self.session.headers.pop('Connection', None)
        api_url = self.get_api_url()
        if not api_url:
            logger.error(f'@{username} 💔 API URL not found')
            return
        search_auctions = {'type': 'usernames', 'query': username, 'method': 'searchAuctions'}
        response = self.session.post(api_url, data=search_auctions)
        response_data = response.json()

        if not isinstance(response_data, dict):
            logger.debug(f'@{username} 💔 Response is not a dict (too many requests. retrying {count} ...)')
            time.sleep(10)
            return self.check_fragment_api(username, count - 1)
        if not response_data.get('html'):
            logger.debug(f'@{username} 💔 Request to fragment API failed. Retrying {count} ...')
            time.sleep(6)
            return self.check_fragment_api(username, count - 1)
        tree = html.fromstring(response_data.get('html'))
        xpath_expression = '//div[contains(@class, "tm-value")]'
        username_data = tree.xpath(xpath_expression)[:3]
        if len(username_data) < 3:
            logger.error(f'@{username} 💔 Not enough username data')
            return
        username_tag = username_data[0].text_content()
        status = username_data[2].text_content()
        price = username_data[1].text_content()
        if username_tag[1:] != username:
            logger.error(f'@{username} 💔 Username not found in response')
            return
        if price.isdigit():
            logger.error(f'@{username} 💸 {status} on fragment for {price}💎')
            return
        user_info = self.get_user(username, api_url)

        if not user_info:
            logger.critical(f'{username_tag} 👤 User')
            return
        elif PREMIUM_USER in user_info:
            logger.error(f'{username_tag} 👑 Premium User')
            return
        elif CHANNEL in user_info:
            logger.error(f'{username_tag} 📢 Channel')
            return
        if user_info == NOT_FOUND and status == 'Unavailable':
            entity = self.get_telegram_web_user(username)
            if not entity:
                logger.critical(f'✅ {username_tag} Maybe Free or Reserved ✅')
                return True
            logger.critical(f'🔒 {username_tag} Premium User with privacy settings 🔒')
            return

        elif 'Bad request' in user_info:
            logger.error(f'{username_tag} 💔 Bad request')
            return
        else:
            logger.error(f'{username_tag} 👀 Unknown api behaviour')
            logger.debug(f'@{username} | Unknown api behaviour | {user_info} | {status}')

    def check(self, username):
        msg = f'@{username} '
        if not re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{4,31}$').match(username):
            logger.info(msg + '💀  Not allowed')
            return
        if username.lower() in RESERVED_WORDS:
            logger.info(msg + '💀 Reserved')
            return
        result = self.check_fragment_api(username.lower())
        time.sleep(5)
        return result

    def run(self, multithread=True):

        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            future_to_username = {executor.submit(self.check, username): username for username in self.usernames}

            for future in as_completed(future_to_username):
                logger.debug(future)
                username = future_to_username[future]
                try:
                    data = future.result()
                except Exception as exc:
                    logger.exception(fr'{username} generated an exception {exc.__class__.__name__}')
                else:
                    logger.debug(fr'{username} page is {data} bytes')

        if multithread:
            executor = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
            executor.map(self.check, self.usernames)
        else:
            [self.check(username) for username in self.usernames]


def parse_args():
    parser = argparse.ArgumentParser(description="Check Telegram usernames.")
    parser.add_argument('--file', type=str, required=False, help='URL to the input file containing usernames')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    return parser.parse_args()


def main():
    args = parse_args()
    checker = TelegramUsernameChecker(file_path=args.file, verbose=args.verbose)
    checker.load()
    checker.run()


if __name__ == "__main__":
    main()
