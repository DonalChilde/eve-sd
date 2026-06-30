-- Table definitions for the sde export to sqlite db.

-- This table is used for dataset entries where the record key is an integer.
CREATE TABLE IF NOT EXISTS DatasetRecordsInt (
    row_id        INTEGER PRIMARY KEY,
    dataset_name  TEXT    NOT NULL, -- The name of the dataset this record belongs to.
    record_key    INTEGER NOT NULL, -- This is the dict key from the imported record.
    record_bytes   BLOB    NOT NULL, -- The entire record as bytes.
    UNIQUE(record_key, dataset_name)
) STRICT;

-- This table is used for dataset entries where the record key is a string.
CREATE TABLE IF NOT EXISTS DatasetRecordsStr (
    row_id        INTEGER PRIMARY KEY,
    dataset_name  TEXT    NOT NULL, -- The name of the dataset this record belongs to.
    record_key    TEXT    NOT NULL, -- This is the dict key from the imported record.
    record_bytes   BLOB    NOT NULL, -- The entire record as bytes.
    UNIQUE(record_key, dataset_name)
) STRICT;

CREATE TABLE IF NOT EXISTS DatasetKeyType (
    row_id               INTEGER PRIMARY KEY,
    dataset_name         TEXT    NOT NULL UNIQUE, -- The name of the dataset.
    key_type             TEXT    NOT NULL -- The type of the record key, either 'int' or 'str'.
) STRICT;

CREATE TABLE IF NOT EXISTS SdeMetadata (
    row_id        INTEGER PRIMARY KEY,
    buildNumber   TEXT    NOT NULL UNIQUE, -- The build number of the sde datasets.
    releaseDate   TEXT    NOT NULL, -- The release date of the sde datasets.
    source_format TEXT    NOT NULL, -- The source format of the sde datasets, either 'yaml' or 'jsonl'.
    source_media  TEXT    NOT NULL -- The source media of the sde datasets.
) STRICT;

CREATE TABLE IF NOT EXISTS DatabaseSettings (
    row_id               INTEGER PRIMARY KEY DEFAULT 1,
    serialization_format TEXT, -- The serialization format used for storing records in the database, either 'yaml', 'json', or 'pickle'.
    CONSTRAINT singleton_row CHECK (row_id = 1)
) STRICT;