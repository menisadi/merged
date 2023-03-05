SELECT timestamp, filename, maid, hh_id, iiqid, partner_id, ip, iscellip,
       cellispid, domain, is_house_ip_or_source_ip, brand, model, os, osversion,
       browser, advertisedbrowser, browserversion, type, is_best_ip
FROM "ariel"."ml_data_2023_02"
WHERE hh_id IN (
  SELECT DISTINCT hh_id
  FROM "ariel"."ml_data_2023_02"
  ORDER BY hh_id
  LIMIT 100000
) AND 
  timestamp IS NOT NULL AND
  filename IS NOT NULL AND
  maid IS NOT NULL AND
  iiqid IS NOT NULL AND
  partner_id IS NOT NULL AND
  ip IS NOT NULL AND
  iscellip IS NOT NULL AND
  cellispid IS NOT NULL AND
  domain IS NOT NULL AND
  is_house_ip_or_source_ip IS NOT NULL AND
  brand IS NOT NULL AND
  model IS NOT NULL AND
  os IS NOT NULL AND
  osversion IS NOT NULL AND
  browser IS NOT NULL AND
  advertisedbrowser IS NOT NULL AND
  browserversion IS NOT NULL AND
  type IS NOT NULL AND
  is_best_ip IS NOT NULL;
