import singer
import singer.metrics as metrics
from singer import metadata
from singer.bookmarks import get_bookmark
from tap_insightly.utility import (
    get_generic,
    get_all_pages,
    get_endpoint,
    formatDate,
)


CAN_FILTER = set(["contacts", "opportunities", "organisations"])
HAS_CUSTOM_FIELDS = set(["contacts", "opportunities"])

# Custom fields are an array, so will become a new table (thanks to target-redshift)
# By default has no relationship to original resource until we add it
def transform_custom_field(id_field, row):
    for c in row["CUSTOMFIELDS"]:
        c[id_field] = row[id_field]
    return row


def handle_basic(resource, schema, id_field, state, mdata):
    extraction_time = singer.utils.now()
    endpoint = get_endpoint(resource)
    bookmark = get_bookmark(state, resource, "since")
    qs = {} if resource not in CAN_FILTER else {"updated_after_utc": bookmark}

    with metrics.record_counter(resource) as counter:
        for page in get_all_pages(resource, endpoint, qs):
            for row in page:
                # Handle custom fields if present
                if resource in HAS_CUSTOM_FIELDS:
                    row = transform_custom_field(id_field, row)

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
