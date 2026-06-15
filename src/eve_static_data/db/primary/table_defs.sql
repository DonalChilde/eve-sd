-- Table definitions for the sde export to sqlite db.

-- This table is used for dataset entries where the record key is an integer.
CREATE TABLE IF NOT EXISTS DatasetRecordsInt (
    id            INTEGER PRIMARY KEY,
    record_key    INTEGER NOT NULL, -- This is the dict key from the imported record.
    dataset_name  TEXT    NOT NULL, -- The name of the dataset this record belongs to.
    record_json   BLOB    NOT NULL, -- The entire record as JSON bytes.
    UNIQUE(record_key, dataset_name)
) STRICT;

-- This table is used for dataset entries where the record key is a string.
CREATE TABLE IF NOT EXISTS DatasetRecordsStr (
    id            INTEGER PRIMARY KEY,
    record_key    TEXT    NOT NULL, -- This is the dict key from the imported record.
    dataset_name  TEXT    NOT NULL, -- The name of the dataset this record belongs to.
    record_json   BLOB    NOT NULL, -- The entire record as JSON bytes.
    UNIQUE(record_key, dataset_name)
) STRICT;

CREATE TABLE IF NOT EXISTS DatasetKeyType (
    id            INTEGER PRIMARY KEY,
    dataset_name  TEXT    NOT NULL UNIQUE, -- The name of the dataset.
    key_type      TEXT    NOT NULL -- The type of the record key, either 'int' or 'str'.
) STRICT;