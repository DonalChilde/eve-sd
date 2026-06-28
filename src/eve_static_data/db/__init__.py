"""Database helpers for the eve_static_data package.

Eve Static Data offers a SQLite database for storing and accessing the SDE data.

This allows for accessing particular records without having to load the entire SDE dataset
into memory, which can be quite large.

Compromises are made in the stored datasets to allow one database definition to
store both yaml and json datasets, which have different data types.

The records are stored as JSON blobs in the database, which allows for storing the data in a single column
without having to define a schema for each dataset. The record key is stored as a separate column, which allows for indexing and querying the records by key.
The record key data type is kept, but sub-dicts in the records are stored as json, which does not
allow for integer keys, so the sub-dict keys are converted to strings.

Records retrieved in a validated format will have the keys converted back to their original data types.
It is up to the user to manage data type conversions when using the raw JSON data.

# TODO describe the specific compromises made for each dataset and format.
# The place for the detailed description might be in a help doc instead of here....
"""
