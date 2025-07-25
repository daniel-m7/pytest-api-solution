pet = {
    "type": "object",
    "required": ["name", "type"],
    "properties": {
        "id": {
            "type": "integer"
        },
        "name": {
            "type": "string"
        },
        "type": {
            "type": "string",
            "enum": ["cat", "dog", "fish"]
        },
        "status": {
            "type": "string",
            "enum": ["available", "sold", "pending"]
        },
    }
}

# add order schema

order = {
    "type": "object",
    "required": ["id", "pet_id", "status"],
    "properties": {
        "id": {
            "type": "string"
        },
        "pet_id": {
            "type": "integer"
        },
        "status": {
            "type": "string",
            "enum": ["available", "sold", "pending"]
        },
    }
}
