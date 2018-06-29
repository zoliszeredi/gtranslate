import logging
import argparse
import uuid
import sys
import socket
import os

from . import messaging


# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


def process_message(message, responses):
    logger.info('  [x] Received {}'.format(message.body))
    response = messaging.deserialize(message.body)
    responses.append(response)


def complete(lines, responses):
    original = sorted(lines)
    answers = sorted([response['original']
                      for response in responses])
    return original == answers


def read_data():
    parser = argparse.ArgumentParser(
        description='Google Translate CLI.'
    )
    parser.add_argument('-f', '--file', type=argparse.FileType('r'),
                        help='Input File', default=sys.stdin)
    parser.add_argument('-l', '--language',
                        help='Language', default='en',
                        choices=('en', 'ro', 'it', 'de'))
    parser.add_argument('-v', '--verbosity', type=int,
                        help='Verbosity', default='0')
    args = parser.parse_args()
    logger.info('Called with {}'.format(args))
    rawlines = args.file.readlines()
    lines = [line.strip()
             for line in rawlines
             if line.strip()]
    return lines, args.language, args.verbosity


def print_responses(responses, verbosity=0):
    formats = {
        0: '{translation}',
        1: '{original}[{olang}] -> {translation}[{tlang}]',
    }
    for response in responses:
        options = {
            'translation': response['translation'],
            'original': response['original'],
            'olang': response['original-language'],
            'tlang': response['translation-language'],
        }
        print (formats[verbosity].format(**options))

def main():
    try:
        timeout = int(os.environ.get('GTD_TIMEOUT'))
    except (ValueError, TypeError):
        timeout = 10
    client_id = '{}'.format(uuid.uuid4())
    lines, language, verbosity = read_data()
    for line in lines:
        messaging.send(
            messaging.serialize({
                'text': line,
                'language': language,
                'client': client_id,
            }),
            'input-queue'
        )
    responses = []
    try:
        messaging.recieve('output-queue-{}'.format(client_id),
                          lambda m: process_message(m, responses),
                          lambda: complete(lines, responses),
                          timeout=timeout)
        print_responses(responses, verbosity)
    except socket.error as error:
        logger.error('Error with gtd: {}'.format(error))


if __name__ == '__main__':
    main()
