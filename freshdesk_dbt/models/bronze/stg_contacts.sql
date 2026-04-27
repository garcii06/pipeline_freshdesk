WITH source AS (
    SELECT * 
      FROM {{ source('raw', 'contacts') }}
),
parsed AS (
    SELECT PARSE_JSON(_raw):id::INTEGER                 AS id
        , PARSE_JSON(_raw):active::BOOLEAN              AS active
        , PARSE_JSON(_raw):address::VARCHAR             AS address
        , PARSE_JSON(_raw):name::VARCHAR                AS name
        , PARSE_JSON(_raw):description::VARCHAR         AS description
        , PARSE_JSON(_raw):email::VARCHAR               AS email
        , PARSE_JSON(_raw):job_title::VARCHAR           AS job_title
        , PARSE_JSON(_raw):language::VARCHAR            AS language
        , PARSE_JSON(_raw):mobile::VARCHAR              AS mobile
        , PARSE_JSON(_raw):phone::VARCHAR               AS phone
        , PARSE_JSON(_raw):time_zone::VARCHAR           AS time_zone
        , PARSE_JSON(_raw):time_zone::VARCHAR           AS twitter_id
        , PARSE_JSON(_raw):custom_fields                AS custom_fields
        , PARSE_JSON(_raw):facebook_id::VARCHAR         AS facebook_id
        , PARSE_JSON(_raw):created_at::TIMESTAMP_TZ     AS created_at
        , PARSE_JSON(_raw):updated_at::TIMESTAMP_TZ     AS updated_at
        , PARSE_JSON(_raw):csat_rating::INTEGER         AS csat_rating
        , PARSE_JSON(_raw):preferred_source::VARCHAR    AS preferred_source
        , PARSE_JSON(_raw):company_id::INTEGER          AS company_id
        , PARSE_JSON(_raw):unique_external_id::VARCHAR  AS unique_external_id
        , PARSE_JSON(_raw):first_name::VARCHAR          AS first_name
        , PARSE_JSON(_raw):last_name::VARCHAR           AS last_name
        , PARSE_JSON(_raw):visitor_id::VARCHAR          AS visitor_id
        , PARSE_JSON(_raw):org_contact_id::INTEGER      AS org_contacorg_contact_idt_id_str
        , PARSE_JSON(_raw):org_contact_id_str::VARCHAR  AS org_contact_id_str
        , PARSE_JSON(_raw):other_phone_numbers          AS other_phone_numbers
        , PARSE_JSON(_raw):social_handler               AS social_handler
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