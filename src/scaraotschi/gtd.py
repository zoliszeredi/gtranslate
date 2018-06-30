"""
Daemon process that handle's requests from input queue
"""
import multiprocessing
import logging
import os

import daemon
import googletrans

from . import messaging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


def translate(line, dest_lang='en', translator=None, timeout=5):
    "See: https://py-googletrans.readthedocs.io/en/latest/"
    translator = (translator or
                  googletrans.Translator(timeout=timeout))
    translation = translator.translate(line, dest=dest_lang)
    return translation



def process_message(message):
    input_ = messaging.deserialize(message.body)
    translation = translate(input_['text'],
                            input_['language'])
    output_ = {
        'translation': translation.text,
        'translation-language': input_['language'],
        'original': input_['text'],
        'original-language': translation.src,
        'client': input_['client'],
    }
    return messaging.send(messaging.serialize(output_),
                          queue='output-queue-{}'.format(input_['client']))


def task(message, pool):
    process = multiprocessing.Process(
        target=process_message,
        args=(message, ),
    )
    process.start()
    pool.append(process)


def all_processes_finished(pool, maxsize):
    for process in pool:
        if process.is_alive() or process.exitcode is not None:
            finished = False
            break
    else:
        finished = len(pool) > 0
    return finished and len(pool) > maxsize


def mainloop(maxsize):
    while True:
        process_pool = []
        messaging.recieve(
            queue='input-queue',
            callback=lambda m: task(m, process_pool),
            done=lambda: all_processes_finished(process_pool, maxsize)
        )
        for process in process_pool:
            process.join()


def main():
    try:
        queries_per_sec = int(os.environ.get('QUERIES_PER_SEC'))
    except (ValueError, TypeError):
        queries_per_sec = 16
    with daemon.DaemonContext():
        mainloop(queries_per_sec)


if __name__ == '__main__':
    main()
