import logging
import argparse
import uuid

from . import messaging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


def process_message(message, responses):
    logger.info('  [x] Received {}'.format(message.body))
    response = messaging.deserialize(message.body)
    responses[response['original']] = response['translation']


def main():
    parser = argparse.ArgumentParser(
        description='Google Translate CLI.'
    )
    parser.add_argument('-f', '--file', help='Input File')
    parser.add_argument('-l', '--language', help='Language')
    args = parser.parse_args()
    logger.info('Called with {}'.format(args))
    with open(args.file) as fp:
        lines = fp.readlines()
    client_id = '{}'.format(uuid.uuid4())
    for line in lines:
        messaging.send(
            messaging.serialize({
                'text': line.strip(),
                'language': args.language,
                'client': client_id,
            }),
            'input-queue'
        )
    responses = {}
    messaging.recieve('output-queue-{}'.format(client_id),
                      lambda x: process_message(x, responses),
                      lambda: len(responses) == len(lines))


if __name__ == '__main__':
    main()
