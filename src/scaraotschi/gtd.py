import multiprocessing.pool
import logging
import os

import daemon
import googletrans

from . import messaging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)
process_pool = multiprocessing.pool.Pool(
    processes=os.environ.get('QUERIES_PER_SEC', 16)
)


def translate(line, dest_lang='en'):
    "See: https://py-googletrans.readthedocs.io/en/latest/"
    translator = googletrans.Translator()
    translation = translator.translate(line, dest=dest_lang)
    output = translation.text
    return output



def main():
    messaging.recieve(
        queue='input_queue',
        callback=lambda x: messaging.send(
            '{}:{}'.format(messaging.hash(x.body), translate(x.body)),
            queue='output_queue'
        )
    )



if __name__ == '__main__':
    main()
