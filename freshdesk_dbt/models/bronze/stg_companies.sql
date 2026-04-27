WITH source AS (
    SELECT * 
      FROM {{ source('raw', 'companies') }}
),
parsed AS (
    SELECT PARSE_JSON(_raw):id::INTEGER                 AS id
        , PARSE_JSON(_raw):name::VARCHAR                AS name
        , PARSE_JSON(_raw):description::VARCHAR         AS description
        , PARSE_JSON(_raw):note::VARCHAR                AS note
        , PARSE_JSON(_raw):domains                      AS domains
        , PARSE_JSON(_raw):created_at::TIMESTAMP_TZ     AS created_at
        , PARSE_JSON(_raw):updated_at::TIMESTAMP_TZ     AS updated_at
        , PARSE_JSON(_raw):custom_fields                AS custom_fields
        , PARSE_JSON(_raw):health_score::VARCHAR        AS health_score
        , PARSE_JSON(_raw):account_tier::VARCHAR        AS account_tier
        , PARSE_JSON(_raw):renewal_date::TIMESTAMP_TZ   AS renewal_date
        , PARSE_JSON(_raw):industry::VARCHAR            AS industry
        , PARSE_JSON(_raw):org_company_id::VARCHAR      AS org_company_id
        , _loaded_at
        , _source
        , _batch_id
    FROM source
), deduped AS(
    SELECT *
         , ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) as n_row
      FROM parsed
)
SELECT * EXCLUDE n_row
  FROM deduped
 WHERE n_row = 1