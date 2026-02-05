from validation.upi_validator import validate_upi
from validation.url_validator import validate_url
from validation.phone_validator import validate_phone

VALIDATORS = {
    "UPI_ID": validate_upi,
    "URL": validate_url,
    "PHONE_NUMBER": validate_phone
}

def validate_entities(entities: list) -> list:
    validated = []

    for entity in entities:
        validator = VALIDATORS.get(entity["type"])

        if validator:
            validated_entity = validator(entity)
            validated.append(validated_entity)
        else:
            # Unknown entity type — pass through unchanged
            validated.append(entity)

    return validated
