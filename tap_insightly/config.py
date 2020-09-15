from tap_insightly.fetch import handle_basic, handle_with_links

ID_FIELDS = {
    "contacts": "CONTACT_ID",
    "opportunities": "OPPORTUNITY_ID",
    "organisations": "ORGANISATION_ID",
    "pipelines": "PIPELINE_ID",
    "pipeline_stages": "STAGE_ID",
}

CAN_FILTER = set(["contacts", "opportunities", "organisations"])

SYNC_FUNCTIONS = {
    "contacts": handle_with_links("contacts"),
    "opportunities": handle_with_links("opportunities"),
    "organisations": handle_with_links("organisations"),
    "pipelines": handle_basic("pipelines"),
    "pipeline_stages": handle_basic("pipeline_stages"),
}
