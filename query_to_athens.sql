SELECT num_distinct_iiqid, COUNT(*) as num_groups
FROM (
    SELECT hh_id, brand, model, advertisedbrowser,  browser, os, COUNT(DISTINCT iiqid) as num_distinct_iiqid
    FROM "ariel"."ml_data_2023_02"
    GROUP BY hh_id, brand, model, advertisedbrowser,browser, os
) subquery
GROUP BY num_distinct_iiqid;

