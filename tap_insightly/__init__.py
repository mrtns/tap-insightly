import os
import json
import singer
from singer import metadata

from tap_insightly.utility import get_abs_path, session
from tap_insightly.config import ID_FIELDS, HAS_LINKS
from tap_insightly.fetch import handle_resource

logger = singer.get_logger()

REQUIRED_CONFIG_KEYS = ["api_key"]


def load_schemas():
    schemas = {}

    for filename in os.listdir(get_abs_path("schemas")):
        path = get_abs_path("schemas") + "/" + filename
        file_raw = filename.replace(".json", "")
        with open(path) as file:
            schemas[file_raw] = json.load(file)

    return schemas


def populate_metadata(schema_name, schema):
    mdata = metadata.new()
    mdata = metadata.write(mdata, (), "table-key-properties", [ID_FIELDS[schema_name]])

    for field_name in schema["properties"].keys():
        mdata = metadata.write(
            mdata,
            ("properties", field_name),
            "inclusion",
            "automatic" if field_name == ID_FIELDS[schema_name] else "available",
        )

    return mdata


def get_catalog():
    raw_schemas = load_schemas()
    streams = []

    for schema_name, schema in raw_schemas.items():

        # get metadata for each field
        mdata = populate_metadata(schema_name, schema)

        # create and add catalog entry
        catalog_entry = {
            "stream": schema_name,
            "tap_stream_id": schema_name,
            "schema": schema,
            "metadata": metadata.to_list(mdata),
            "key_properties": [ID_FIELDS[schema_name]],
        }
        streams.append(catalog_entry)

    return {"streams": streams}


def do_discover():
    catalog = get_catalog()
    # dump catalog
    print(json.dumps(catalog, indent=2))


def get_selected_streams(catalog):
    """
    Gets selected streams.  Checks schema's 'selected'
    first -- and then checks metadata, looking for an empty
    breadcrumb and mdata with a 'selected' entry
    """
    selected_streams = []
    for stream in catalog["streams"]:
        stream_metadata = stream["metadata"]
        if stream["schema"].get("selected", False):
            selected_streams.append(stream["tap_stream_id"])
        else:
            for entry in stream_metadata:
                # stream metadata will have empty breadcrumb
                if not entry["breadcrumb"] and entry["metadata"].get("selected", None):
                    selected_streams.append(stream["tap_stream_id"])

    return selected_streams


def get_stream_from_catalog(stream_id, catalog):
    for stream in catalog["streams"]:
        if stream["tap_stream_id"] == stream_id:
            return stream
    return None


def do_sync(config, state, catalog):
    # Insightly API uses basic auth. Pass API key as the username and leave the password blank
    session.auth = (config["api_key"], "")

    selected_stream_ids = get_selected_streams(catalog)

    singer.write_state(state)

    links_stream = next(s for s in catalog["streams"] if s["tap_stream_id"] == "links")
    links_schema = links_stream["schema"]

    for stream in catalog["streams"]:
        stream_id = stream["tap_stream_id"]
        stream_schema = stream["schema"]
        mdata = stream["metadata"]

        # links are a special case
        if stream_id == "links":
            continue

        # if stream is selected, write schema and sync
        if stream_id in selected_stream_ids:
            singer.write_schema(stream_id, stream_schema, stream["key_properties"])

            schemas = {stream_id: stream_schema}
            if stream_id in HAS_LINKS and "links" in selected_stream_ids:
                singer.write_schema(
                    "links", links_schema, links_stream["key_properties"]
                )
                schemas["links"] = links_schema

            state = handle_resource(
                stream_id, schemas, ID_FIELDS[stream_id], state, mdata,
            )

            singer.write_state(state)


@singer.utils.handle_top_exception(logger)
def main():
    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    if args.discover:
        do_discover()
    else:
        catalog = args.properties if args.properties else get_catalog()
        do_sync(args.config, args.state, catalog)


if __name__ == "__main__":
    main()
