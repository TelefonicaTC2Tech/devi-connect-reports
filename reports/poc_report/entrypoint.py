from connect.client import R

from reports.fields import Field, Fields
from reports.utils import get_value

FIELDS = Fields((
    Field('Request ID', lambda r: get_value(r, 'id')),
    Field('Asset External ID', lambda r: get_value(r, 'asset.external_id'))
))


def generate(
    client=None,
    parameters=None,
    progress_callback=None,
    renderer_type=None,
    extra_context_callback=None,
):
    requests = _get_requests(client, parameters)
    progress = 0
    total = requests.count()
    if renderer_type == 'csv':
        yield FIELDS.names()
        progress += 1
        total += 1
        progress_callback(progress, total)

    for request in requests:
        values = FIELDS.process(request)
        if renderer_type == 'json':
            yield dict(zip(FIELDS.json_names(), values))
        else:
            yield values
        progress += 1
        progress_callback(progress, total)


def _get_requests(client, parameters):
    all_connections = ['test']

    query = R()
    query &= R().created.ge(parameters['date']['after'])
    query &= R().created.le(parameters['date']['before'])

    if parameters.get('product') and parameters['product']['all'] is False:
        query &= R().asset.product.id.oneof(parameters['product']['choices'])

    return client.requests.filter(query).all()
