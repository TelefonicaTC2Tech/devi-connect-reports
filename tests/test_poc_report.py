# -*- coding: utf-8 -*-
#
# Copyright (c) 2022, TCCT
# All rights reserved.
#
from reports.poc_report.entrypoint import generate
from datetime import datetime
from reports.utils import get_value
from reports.fields import Field, Fields


FIELDS = Fields((
    Field('Request ID', lambda r: get_value(r, 'id')),
    Field('Asset External ID', lambda r: get_value(r, 'asset.external_id'))
))


def test_poc_report_csv(
    mocker,
    progress,
    sync_client_factory,
    response_factory,
    poc_response,
    extra_context_callback,
):

    responses = []
    # create a response for a count call

    responses.append(response_factory(count=100))

    # create response for a collection

    responses.append(response_factory(
        query='and(ge(created,2022-11-11T00:00:00),le(created,2022-11-12T00:00:00))',
        select=None,
        value=poc_response,
    ))

    client = sync_client_factory(responses)

    parameters = {
        'date': {
            'after': '2022-11-11T00:00:00',
            'before': '2022-11-12T00:00:00',
        },
        'product': {
            'all': True
        }
    }
    generator = generate(
        client,
        parameters,
        progress,
        renderer_type='csv',
        extra_context_callback=mocker.MagicMock(),
    )

    expected = []
    first_row = (
        'Request ID',
        'Asset External ID'
    )
    expected.append((
        map(lambda x: x, first_row)
    ))
    for row in poc_response:
        expected.append((
            map(lambda x: x, (row['id'], row['asset']['external_id']))
        ))

    index = 0
    items = list(generator)

    print('items: '+str(len(items)))
    for element in items:
        assert list(element) == list(expected[index])
        index += 1
