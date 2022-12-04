DECLARE datasets ARRAY<string>;
DECLARE query string;
DECLARE counter INT64 DEFAULT 0;
DECLARE totalDatasets INT64;

SET datasets = ARRAY(select schema_name from `<<project-id>>.region-<<region-id>>.INFORMATION_SCHEMA.SCHEMATA`);
SET query = "SELECT * FROM (";
SET totalDatasets = ARRAY_LENGTH(datasets);

WHILE counter < totalDatasets - 1 DO
  SET query = CONCAT(query, "SELECT '", datasets[OFFSET(counter)], "', table_ID, row_count, size_bytes from `on-prem-project-337210.", datasets[OFFSET(counter)], '.__TABLES__` UNION ALL ');
  SET counter = counter + 1;
END WHILE;

SET query = CONCAT(query, "SELECT '", datasets[ORDINAL(totalDatasets)], "', table_ID, row_count, size_bytes from `on-prem-project-337210.", datasets[ORDINAL(totalDatasets)], '.__TABLES__` )');

EXECUTE IMMEDIATE query;
