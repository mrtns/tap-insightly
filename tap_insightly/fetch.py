import singer
import singer.metrics as metrics
from singer import metadata
from tap_insightly.utility import (
    get_generic,
    get_all_pages,
    get_endpoint,
    formatDate,
)


def handle_basic(resource, schema, state, mdata):
    extraction_time = singer.utils.now()
    endpoint = get_endpoint(resource)

    with metrics.record_counter(resource) as counter:
        for page in get_all_pages(resource, endpoint):
            for row in page:
                write_record(row, resource, schema, mdata, extraction_time)
                counter.increment()
    return write_bookmark(state, resource, extraction_time)



# More convenient to use but has to all be held in memory, so use write_record instead for resources with many rows
def write_many(rows, resource, schema, mdata, dt):
    with metrics.record_counter(resource) as counter:
        for row in rows:
            write_record(row, resource, schema, mdata, dt)
            counter.increment()


def write_record(row, resource, schema, mdata, dt):
    with singer.Transformer() as transformer:
        rec = transformer.transform(row, schema, metadata=metadata.to_map(mdata))
    singer.write_record(resource, rec, time_extracted=dt)


def write_bookmark(state, resource, dt):
    singer.write_bookmark(state, resource, "since", formatDate(dt))
    return state
