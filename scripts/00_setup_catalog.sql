-- SKY-004: Creación de catálogo, schemas y Volume en Unity Catalog
CREATE CATALOG IF NOT EXISTS skylake COMMENT 'Proyecto SkyLake: trafico aereo';

CREATE SCHEMA IF NOT EXISTS skylake.bronze COMMENT 'Datos crudos';
CREATE SCHEMA IF NOT EXISTS skylake.silver COMMENT 'Datos limpios y tipados';
CREATE SCHEMA IF NOT EXISTS skylake.gold   COMMENT 'Modelo analitico';
CREATE SCHEMA IF NOT EXISTS skylake.ops    COMMENT 'Observabilidad del pipeline';

CREATE VOLUME IF NOT EXISTS skylake.bronze.landing COMMENT 'Archivos crudos de OpenSky';
