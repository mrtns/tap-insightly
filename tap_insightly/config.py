ID_FIELDS = {
    "contacts": "CONTACT_ID",
    "emails": "EMAIL_ID",
    "full_emails": "EMAIL_ID",
    "file_attachments": "FILE_ID",
    "leads": "LEAD_ID",
    "links": "LINK_ID",
    "opportunities": "OPPORTUNITY_ID",
    "organisations": "ORGANISATION_ID",
    "pipelines": "PIPELINE_ID",
    "pipeline_stages": "STAGE_ID",
    "users": "USER_ID",
}

HAS_LINKS = set(["contacts", "leads", "opportunities", "organisations"])
HAS_FULL_EMAILS = set(["emails"])
HAS_FILE_ATTACHMENTS = set(["emails"])
