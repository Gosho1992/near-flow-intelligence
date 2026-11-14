-- Candidate discovery for the one-hop attribution sensitivity.
-- Dataset: bigquery-public-data.crypto_near_mainnet_us
-- Snapshot boundary: height 224285093 (2026-11-13 00:00 UTC).
--
-- This query is deliberately a candidate screen, not an attribution proof:
-- it finds successful native TRANSFER actions from a direct hub recipient to
-- another account, then checks whether that recipient later called the NRR pool.
-- Amount and block ordering must still be reviewed before changing attribution.
WITH direct_hub_recipients AS (
  SELECT DISTINCT receiver_account_id AS account
  FROM `bigquery-public-data.crypto_near_mainnet_us.transactions`
  WHERE block_date BETWEEN '2026-09-20' AND '2026-11-13'
    AND signer_account_id = '23ced4300a4bf282bf94a4fcd2b0af32ad291ef531f544f6d7d283e8ff1e684a'
),
one_hop_candidates AS (
  SELECT
    t.receiver_account_id AS candidate_account,
    t.signer_account_id AS direct_parent_account,
    t.transaction_hash AS candidate_funding_tx,
    t.block_height AS candidate_funding_height,
    t.block_date AS candidate_funding_date,
    t.status AS candidate_funding_status,
    ra.args AS candidate_funding_args
  FROM `bigquery-public-data.crypto_near_mainnet_us`.transactions t
  JOIN `bigquery-public-data.crypto_near_mainnet_us`.receipt_actions ra
    ON ra.receipt_id = t.converted_into_receipt_id
   AND ra.block_date BETWEEN '2026-09-20' AND '2026-11-14'
  JOIN direct_hub_recipients d
    ON d.account = t.signer_account_id
  WHERE t.block_date BETWEEN '2026-09-20' AND '2026-11-13'
    AND t.block_height < 224285093
    AND t.status = 'SUCCESS'
    AND ra.action_kind = 'TRANSFER'
    AND t.receiver_account_id IS NOT NULL
    AND t.receiver_account_id NOT IN (
      '23ced4300a4bf282bf94a4fcd2b0af32ad291ef531f544f6d7d283e8ff1e684a',
      'bitwise_2.poolv1.near'
    )
),
pool_calls AS (
  SELECT DISTINCT
    t.transaction_hash AS pool_tx_hash,
    t.signer_account_id AS pool_signer,
    t.block_height AS pool_tx_height,
    t.block_date AS pool_tx_date,
    t.status AS pool_tx_status,
    JSON_VALUE(r.args, '$.method_name') AS pool_method
  FROM `bigquery-public-data.crypto_near_mainnet_us.transactions` t
  LEFT JOIN `bigquery-public-data.crypto_near_mainnet_us.receipt_actions` r
    ON r.receipt_id = t.converted_into_receipt_id
   AND r.block_date BETWEEN '2026-09-20' AND '2026-11-14'
  WHERE t.block_date BETWEEN '2026-09-20' AND '2026-11-13'
    AND t.receiver_account_id = 'bitwise_2.poolv1.near'
    AND t.block_height < 224285093
    AND t.status = 'SUCCESS'
    AND JSON_VALUE(r.args, '$.method_name') IN ('deposit_and_stake', 'unstake_all', 'withdraw_all')
),
candidate_paths AS (
  SELECT
    p.*,
    CASE
      WHEN d.account IS NOT NULL THEN 'direct_hub_recipient'
      WHEN o.candidate_account IS NOT NULL THEN 'one_hop_candidate'
      ELSE 'unclassified'
    END AS path_class,
    o.direct_parent_account,
    o.candidate_funding_tx,
    o.candidate_funding_height,
    o.candidate_funding_date
  FROM pool_calls p
  LEFT JOIN direct_hub_recipients d
    ON d.account = p.pool_signer
  LEFT JOIN one_hop_candidates o
    ON o.candidate_account = p.pool_signer
   AND o.candidate_funding_height < p.pool_tx_height
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY p.pool_tx_hash
    ORDER BY IF(o.candidate_funding_height IS NULL, -1, o.candidate_funding_height) DESC
  ) = 1
)
SELECT *
FROM candidate_paths
WHERE path_class IN ('direct_hub_recipient', 'one_hop_candidate')
ORDER BY pool_tx_height, pool_tx_hash;
