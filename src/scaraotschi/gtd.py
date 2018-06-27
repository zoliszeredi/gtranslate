import multiprocessing.pool
import logging
import queue
import os

import daemon
import googletrans

from . import messaging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)
QUERIES_PER_SEC = os.environ.get('QUERIES_PER_SEC', 16)



def translate(line, dest_lang='en', translator=None):
    "See: https://py-googletrans.readthedocs.io/en/latest/"
    translator = translator or googletrans.Translator()
    translation = translator.translate(line, dest=dest_lang)
    output = translation.text
    return output



def process_message(message):
    input_ = messaging.deserialize(message.body)
    output_ = {
        'translation': translate(input_['text'],
                                 input_['language']),
        'original': input_['text'],
    }
    return messaging.send(messaging.serialize(output_),
                          queue='output-queue-{}'.format(input_['client']))


def main():
    process_pool = multiprocessing.pool.Pool()
    input_queue = queue.Queue(maxsize=process_pool._processes)
    messaging.recieve(
        queue='input-queue',
        callback=process_message
    )



if __name__ == '__main__':
    with daemon.DaemonContext:
        main()
