import multiprocessing
import logging
import os
import signal

import daemon
import googletrans

from . import messaging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)
QUERIES_PER_SEC = os.environ.get('QUERIES_PER_SEC', 16)
TRANSLATE_TIMEOUT = 3


def translate(line, dest_lang='en', translator=None):
    "See: https://py-googletrans.readthedocs.io/en/latest/"
    translator = (translator or
                  googletrans.Translator(timeout=TRANSLATE_TIMEOUT))
    translation = translator.translate(line, dest=dest_lang)
    output = translation.text
    return output



def process_message(message):
    input_ = messaging.deserialize(message.body)
    output_ = {
        'translation': translate(input_['text'],
                                 input_['language']),
        'original': input_['text'],
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


def all_processes_finished(pool):
    for process in pool:
        if process.is_alive() or process.exitcode is not None:
            finished = False
            break
    else:
        finished = len(pool) > 0
    return finished


def mainloop():
    while True:
        process_pool = []
        messaging.recieve(
            queue='input-queue',
            callback=lambda m: task(m, process_pool),
            done=lambda: all_processes_finished(process_pool)
        )
        for process in process_pool:
            process.join()


def main():
    with daemon.DaemonContext():
        mainloop()


if __name__ == '__main__':
    main()
