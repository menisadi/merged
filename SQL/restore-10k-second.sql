SELECT t1.*
FROM "ariel"."ml_data_2023_02" t1
JOIN (
  SELECT hh_id FROM "ariel"."ml_data_2023_02"
  GROUP BY hh_id
  ORDER BY RAND()
  LIMIT 10000
) t2
ON t1.hh_id = t2.hh_id;
