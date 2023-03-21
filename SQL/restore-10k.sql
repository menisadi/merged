SELECT * FROM "ariel"."ml_data_2023_02" WHERE 
hh_id IN (
    SELECT DISTINCT hh_id FROM "ariel"."ml_data_2023_02" 
    ORDER BY RAND() 
    LIMIT 10000
)