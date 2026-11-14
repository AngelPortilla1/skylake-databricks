CREATE OR REFRESH STREAMING TABLE skylake.bronze.flight_states_raw
COMMENT 'Snapshots crudos de OpenSky (states/all). Un registro por archivo.'
AS SELECT
  *,
  current_timestamp()              AS _ingested_at,
  _metadata.file_path              AS _source_file,
  _metadata.file_modification_time AS _source_modified_at
FROM STREAM read_files(
  '/Volumes/skylake/bronze/landing/opensky/states/',
  format => 'json',
  multiLine => true
);

CREATE OR REFRESH STREAMING TABLE skylake.bronze.aircraft_db
COMMENT 'Catalogo de aeronaves (snapshot mensual)'
AS SELECT
  *,
  _metadata.file_path              AS _source_file,
  _metadata.file_modification_time AS _source_modified_at,
  current_timestamp()              AS _ingested_at
FROM STREAM read_files(
  '/Volumes/skylake/bronze/landing/reference/aircraft/',
  format => 'csv',
  header => true
);
