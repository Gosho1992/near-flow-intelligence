-- Completeness check run in Google BigQuery (public dataset bigquery-public-data.crypto_near_mainnet_us), 2026-11-13.
-- Independent of this pipeline: it starts from every account the custody hub signed any transaction to
-- (no amount threshold, no ordering rule), and lists every transaction those accounts sent to the NRR pool
-- before the 2026-11-13 00:00 UTC daily height. Expected: exactly the pool transactions in data/out/events.csv.
WITH funded AS (
  SELECT DISTINCT receiver_account_id AS a
  FROM `bigquery-public-data.crypto_near_mainnet_us.transactions`
  WHERE block_date BETWEEN '2026-09-20' AND '2026-11-13'
    AND signer_account_id = '23ced4300a4bf282bf94a4fcd2b0af32ad291ef531f544f6d7d283e8ff1e684a'
), p AS (
  SELECT t.transaction_hash AS h, t.signer_account_id AS s, t.status AS st,
         JSON_VALUE(r.args, '$.method_name') AS m
  FROM `bigquery-public-data.crypto_near_mainnet_us.transactions` t
  LEFT JOIN `bigquery-public-data.crypto_near_mainnet_us.receipt_actions` r
    ON r.receipt_id = t.converted_into_receipt_id AND r.block_date BETWEEN '2026-09-20' AND '2026-11-14'
  WHERE t.block_date BETWEEN '2026-09-20' AND '2026-11-13'
    AND t.receiver_account_id = 'bitwise_2.poolv1.near'
    AND t.block_height < 224285093
    AND t.signer_account_id IN (SELECT a FROM funded)
)
SELECT m, st, COUNT(DISTINCT h) AS n, COUNT(DISTINCT s) AS accts, STRING_AGG(DISTINCT h ORDER BY h) AS hashes
FROM p GROUP BY 1, 2 ORDER BY 3 DESC
