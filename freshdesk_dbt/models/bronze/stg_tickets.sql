WITH source AS (
    SELECT * 
      FROM {{ source('raw', 'tickets') }}
),
parsed AS (
    SELECT PARSE_JSON(_raw):cc_emails                   AS cc_emails
        , PARSE_JSON(_raw):fwd_emails                   AS fwd_emails
        , PARSE_JSON(_raw):reply_cc_emails              AS reply_cc_emails
        , PARSE_JSON(_raw):ticket_cc_emails             AS ticket_cc_emails
        , PARSE_JSON(_raw):fr_escalated::BOOLEAN        AS fr_escalated
        , PARSE_JSON(_raw):spam::BOOLEAN                AS spam
        , PARSE_JSON(_raw):email_config_id::INTEGER     AS email_config_id
        , PARSE_JSON(_raw):group_id::INTEGER            AS group_id
        , PARSE_JSON(_raw):priority::INTEGER            AS priority
        , PARSE_JSON(_raw):requester_id::INTEGER        AS requester_id
        , PARSE_JSON(_raw):responder_id::INTEGER        AS responder_id
        , PARSE_JSON(_raw):source::INTEGER              AS source
        , PARSE_JSON(_raw):company_id::INTEGER          AS company_id
        , PARSE_JSON(_raw):status::INTEGER              AS status
        , PARSE_JSON(_raw):subject::VARCHAR             AS subject
        , PARSE_JSON(_raw):association_type::INTEGER    AS association_type
        , PARSE_JSON(_raw):support_email::VARCHAR       AS support_email
        , PARSE_JSON(_raw):to_emails                    AS to_emails
        , PARSE_JSON(_raw):product_id::INTEGER          AS product_id
        , PARSE_JSON(_raw):id::INTEGER                  AS id
        , PARSE_JSON(_raw):type::VARCHAR                AS type
        , PARSE_JSON(_raw):due_by::TIMESTAMP_TZ         AS due_by
        , PARSE_JSON(_raw):fr_due_by::TIMESTAMP_TZ      AS fr_due_by
        , PARSE_JSON(_raw):is_escalated::BOOLEAN        AS is_escalated
        , PARSE_JSON(_raw):custom_fields                AS custom_fields
        , PARSE_JSON(_raw):created_at::TIMESTAMP_TZ     AS created_at
        , PARSE_JSON(_raw):updated_at::TIMESTAMP_TZ     AS updated_at
        , PARSE_JSON(_raw):associated_tickets_count::INTEGER  AS associated_tickets_count
        , PARSE_JSON(_raw):tags                         AS tags
        , PARSE_JSON(_raw):structured_description       AS structured_description
        , PARSE_JSON(_raw):form_id::INTEGER             AS form_id
        , PARSE_JSON(_raw):nr_due_by::TIMESTAMP_TZ      AS nr_due_by
        , PARSE_JSON(_raw):nr_escalated::BOOLEAN        AS nr_escalated
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