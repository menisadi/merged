SELECT timestamp, filename, maid, hh_id, iiqid, partner_id, ip, iscellip,
       cellispid, domain, is_house_ip_or_source_ip, brand, model, os, osversion,
       browser, advertisedbrowser, browserversion, type, is_best_ip
FROM (
  SELECT timestamp, filename, maid, hh_id, iiqid, partner_id, ip, iscellip,
         cellispid, domain, is_house_ip_or_source_ip, brand, model, os, osversion,
         browser, advertisedbrowser, browserversion, type, is_best_ip,
         COUNT(DISTINCT iiqid) OVER (
           PARTITION BY hh_id, brand, model, os, browser, advertisedbrowser
         ) AS iiqid_count
  FROM "ariel"."ml_data_2023_02"
  WHERE hh_id IN (
    SELECT DISTINCT hh_id
    FROM "ariel"."ml_data_2023_02"
    ORDER BY hh_id
    LIMIT 100000
  )
  AND osversion REGEXP '^[0-9]+(\.[0-9]+)*$'
) t
WHERE t.iiqid_count > 1;

