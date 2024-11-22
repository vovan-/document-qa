select
  id,
  name,
  dp_create_timestamp AS create_at,
  picture_url,
  owners,
  users,
  CURRENT_TIMESTAMP AS dp_create_timestamp,
  CURRENT_TIMESTAMP AS dp_update_timestamp
FROM
  ${extractedData}