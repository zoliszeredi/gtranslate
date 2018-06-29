import logging
import json

import amqp.connection
import amqp.channel
import amqp.basic_message


# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__file__)


def get_channel(queue):
    connection = amqp.connection.Connection()
    connection.connect()
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    return channel


def serialize(dict_):
    return json.dumps(dict_)

def deserialize(bytes_):
    return json.loads(bytes_)


def send(body, queue):
    channel = get_channel(queue)
    message = amqp.basic_message.Message(body=body, delivery_mode=2)
    channel.basic_publish(message, routing_key=queue)
    logger.info(' [x] Sent {}'.format(message.body))


def recieve(queue, callback, done=None, **kwargs):
    channel = get_channel(queue)
    channel.basic_consume(callback=callback, queue=queue, no_ack=True)
    logger.info('  [*] Waiting for messages; exit with CTRL-C ')
    while done is None or not done():
        channel.connection.drain_events(**kwargs)
