from behave import *
from hamcrest import *

from environment import HOST, RABBIT_PORT

import pika
import requests
import unittest

TEST_QUEUE = 'test_queue'

@when('a GET request is made to the simple webserver')
def a_GET_request_is_made_to_the_simple_webserver(context):
    context.response = requests.get(url = "http://" + context.server.host + ":" + str(context.server.get_exposedPort()))


@when('a POST request is made to the simple webserver')
def a_POST_request_is_made_to_the_simple_webserver(context):
    context.payload = '{"payload": "This is a test"}'

    context.response = requests.post(
            url = "http://" + context.server.host + ":" + str(context.server.get_exposedPort()), 
            data = context.payload
    )


@then('the webserver will respond with a HTTP status of "{statusCode}"')
def the_webserver_will_respond_with_a_HTTP_status_of(context, statusCode):
    assert_that(context.response.status_code, equal_to(int(statusCode)))


@then('the response body will contain "{body}"')
def the_response_body_will_contain(context, body):
    assert_that(context.response.text, equal_to(body))


@then('the response body will be empty')
def the_response_body_will_be_empty(context):
    the_response_body_will_contain(context, '')


@then('the request body is added to the RabbitMQ queue')
def the_request_body_is_added_to_the_RabbitMQ_queue(context):
    parameters = pika.ConnectionParameters(host = HOST, 
                                           port = context.rabbit.get_exposed_port(RABBIT_PORT))

    with pika.BlockingConnection(parameters) as connection:
        channel = connection.channel()
        channel.queue_declare(TEST_QUEUE)

        for i in range(30):
            message = channel.basic_get(TEST_QUEUE, auto_ack = True)

            if message[2] != None:
                assert_that(message[2].decode("utf-8"), equal_to(context.payload))
                break
        else:
            fail('Expected message was not received on queue')
