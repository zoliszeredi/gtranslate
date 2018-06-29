import logging
import argparse
import uuid
import time

from . import messaging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


def process_message(message, responses):
    logger.info('  [x] Received {}'.format(message.body))
    response = messaging.deserialize(message.body)
    responses.append(response)


def complete_or_timeout(lines, responses, has_timedout):
    original = sorted(lines)
    answers = sorted([response['original']
                      for response in responses])
    return (has_timedout() or original == answers)


def timedout(start, seconds):
    def check(now=None):
        now = now or time.time()
        result = (now - start) > seconds
        if result:
            logger.info('Timeout {} > {}'.format(now-start, seconds))
        return result
    return check


def main():
    parser = argparse.ArgumentParser(
        description='Google Translate CLI.'
    )
    parser.add_argument('-f', '--file', help='Input File')
    parser.add_argument('-l', '--language', help='Language')
    args = parser.parse_args()
    logger.info('Called with {}'.format(args))
    with open(args.file) as fp:
        lines = [line.strip() for line in fp.readlines()]
    client_id = '{}'.format(uuid.uuid4())
    for line in lines:
        messaging.send(
            messaging.serialize({
                'text': line,
                'language': args.language,
                'client': client_id,
            }),
            'input-queue'
        )
    responses = []
    start_time, seconds = time.time(), 10
    messaging.recieve('output-queue-{}'.format(client_id),
                      lambda m: process_message(m, responses),
                      lambda: complete_or_timeout(lines,
                                                  responses,
                                                  timedout(start_time,
                                                           seconds)))


if __name__ == '__main__':
    main()
