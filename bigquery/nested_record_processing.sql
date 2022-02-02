DROP TABLE `sourabhjainceanalytics.demo.customer_master`;

CREATE TABLE `sourabhjainceanalytics.demo.customer_master`
(
id INT64,
name STRING,
company STRING,
contact_details ARRAY<STRUCT<
type STRING,
phone INT64
>>
);

INSERT INTO `sourabhjainceanalytics.demo.customer_master` 
VALUES 
(1,'PersonA','Company-A',[STRUCT('home',1111111111),STRUCT ('mobile',2222222222)]),
(2,'PersonB','Company-B',[STRUCT('home',3333333333),STRUCT ('mobile',4444444444)]),
(3,'PersonC','Company-C',[STRUCT('home',5555555555),STRUCT ('mobile',6666666666)]),
(4,'PersonD','Company-D',[STRUCT('home',7777777777),STRUCT ('mobile',8888888888)]),
(5,'PersonE','Company-E',[STRUCT('home',9999999999),STRUCT ('mobile',1212121212)]),
(6,'PersonF','Company-F',[STRUCT('home',1313131313),STRUCT ('mobile',1414141414)]);

DROP TABLE `sourabhjainceanalytics.demo.customer_incremental_change`;

CREATE TABLE `sourabhjainceanalytics.demo.customer_incremental_change`
(
id INT64,
name STRING,
company STRING,
contact_details ARRAY<STRUCT<
type STRING,
phone INT64
>>
);

--Assuming a new record is to be inserted.

INSERT INTO `sourabhjainceanalytics.demo.customer_incremental_change` 
VALUES 
(7,'PersonG','Company-G',[STRUCT('home',1515151515),STRUCT ('mobile',1616161616)]);

MERGE `sourabhjainceanalytics.demo.customer_master` T
USING (
        SELECT 
          id,
          name,
          company,
          ARRAY_AGG(STRUCT(cd.type,cd.phone)) as contact_details
        FROM `sourabhjainceanalytics.demo.customer_incremental_change` i,
        UNNEST(contact_details) cd
        GROUP BY 
          id,
          name,
          company
       ) S
ON T.id = S.id
WHEN NOT MATCHED THEN
INSERT VALUES (S.id,S.name,S.company,S.contact_details) ;

-- Flush the incremental data
DELETE FROM `sourabhjainceanalytics.demo.customer_incremental_change` WHERE 1=1; 

-- Assuming a child record is added and the same needs to be added.

INSERT INTO `sourabhjainceanalytics.demo.customer_incremental_change` 
VALUES 
(7,'PersonG','Company-G',[STRUCT('fax',1717171717)]);

MERGE `sourabhjainceanalytics.demo.customer_master` T
USING (
        SELECT 
          id,
          name,
          company,
          ARRAY_AGG(STRUCT(cd.type,cd.phone)) as contact_details
        FROM `sourabhjainceanalytics.demo.customer_incremental_change` i,
        UNNEST(contact_details) cd
        GROUP BY 
          id,
          name,
          company
       ) S
ON T.id = S.id
WHEN MATCHED AND S.contact_details IS NOT NULL THEN
UPDATE SET T.contact_details = ARRAY_CONCAT(T.contact_details, S.contact_details);

-- Flush the incremental data
DELETE FROM `sourabhjainceanalytics.demo.customer_incremental_change` WHERE 1=1; 

-- Assuming a child record is added but it dos not have any nested data.

INSERT INTO `sourabhjainceanalytics.demo.customer_incremental_change` 
VALUES 
(7,'PersonG','Company-G',[]);

MERGE `sourabhjainceanalytics.demo.customer_master` T
USING (
        SELECT 
          id,
          name,
          company,
          ARRAY_AGG(STRUCT(cd.type,cd.phone)) as contact_details
        FROM `sourabhjainceanalytics.demo.customer_incremental_change` i,
        UNNEST(contact_details) cd
        GROUP BY 
          id,
          name,
          company
       ) S
ON T.id = S.id
WHEN MATCHED AND S.contact_details IS NOT NULL THEN
UPDATE SET T.contact_details = ARRAY_CONCAT(T.contact_details, S.contact_details);


-- Flush the incremental data
DELETE FROM `sourabhjainceanalytics.demo.customer_incremental_change` WHERE 1=1; 

INSERT INTO `sourabhjainceanalytics.demo.customer_incremental_change` 
VALUES 
(7,'PersonG','Company-G',[STRUCT('mobile2',1818181818),STRUCT('mobile3',2020202020),STRUCT('home',1717171717)]);

DELETE FROM `sourabhjainceanalytics.demo.customer_incremental_change` WHERE id = 8;
INSERT INTO `sourabhjainceanalytics.demo.customer_incremental_change` 
VALUES 
(8,'PersonH','Company-H',[STRUCT('mobile',1919191919)]);


-- Step 1
-- Create an interim table with status
DROP TABLE `sourabhjainceanalytics.demo.customer_incremental_change_interim`;

CREATE TABLE `sourabhjainceanalytics.demo.customer_incremental_change_interim`
(
id INT64,
name STRING,
company STRING,
status STRING,
contact_details ARRAY<STRUCT<
type STRING,
phone INT64
>>
);

INSERT INTO `sourabhjainceanalytics.demo.customer_incremental_change_interim` (id,name,company,status,contact_details)
  WITH incremental AS(
  SELECT  S.id,
          S.name,
          S.company,
          cd.type,
          cd.phone
  FROM 
    `sourabhjainceanalytics.demo.customer_incremental_change` AS S 
    , UNNEST(contact_details) AS cd
  ),
  master AS(
  SELECT  M.id,
          M.name,
          M.company,
          cd.type,
          cd.phone
  FROM `sourabhjainceanalytics.demo.customer_master` AS M 
    , UNNEST(contact_details) AS cd
  )
  SELECT i.id,
         i.name,
         i.company,
         IF(f.id IS NULL,'I','U') as status, 
         ARRAY_AGG(STRUCT(i.type,i.phone)) AS contact_details,
  FROM incremental AS i
  LEFT OUTER JOIN master AS f
  ON i.id = f.id AND i.phone = f.phone
  GROUP BY id,name,company,status;

-- Step 2
-- Perform insert operations at parent and child rows.

MERGE `sourabhjainceanalytics.demo.customer_master` T
USING `sourabhjainceanalytics.demo.customer_incremental_change_interim` S
ON T.id = S.id
WHEN NOT MATCHED THEN
INSERT VALUES (S.id,S.name,S.company,S.contact_details) 
WHEN MATCHED AND S.status = 'I' THEN
UPDATE SET T.contact_details = ARRAY_CONCAT(T.contact_details, S.contact_details);

-- Step 3
-- Update the child nested records.

UPDATE `sourabhjainceanalytics.demo.customer_master` m
SET contact_details = ARRAY
  (
    SELECT AS STRUCT IF(mcd.phone=scd.phone,scd.type,mcd.type) AS type,mcd.phone
    FROM UNNEST(m.contact_details) mcd
  )
FROM `sourabhjainceanalytics.demo.customer_incremental_change_interim` s, UNNEST(s.contact_details) scd
WHERE m.id = s.id
AND   s.status = 'U';
