import logging
import argparse

from . import messaging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


def set_translation(response, output):
    logger.info('  [x] Received {}'.format(response))
    hash_, translation = response.split(':', 1)
    output[hash_] = translation


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
    for line in lines:
        messaging.send(line.strip(), 'input_queue')
    output = {}
    messaging.recieve('output_queue',
                      lambda x: set_translation(x.body, output),
                      lambda: len(output) == len(lines))


if __name__ == '__main__':
    main()
