from tap_insightly.fetch import handle_basic, handle_with_links

ID_FIELDS = {
    "contacts": "CONTACT_ID",
    "opportunities": "OPPORTUNITY_ID",
    "organisations": "ORGANISATION_ID",
    "pipelines": "PIPELINE_ID",
    "pipeline_stages": "STAGE_ID",
}

SYNC_FUNCTIONS = {
    "contacts": handle_with_links,
    "opportunities": handle_with_links,
    "organisations": handle_with_links,
    "pipelines": handle_basic,
    "pipeline_stages": handle_basic,
}
