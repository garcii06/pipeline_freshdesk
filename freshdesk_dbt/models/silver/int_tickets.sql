WITH bronze AS(
    SELECT *
      FROM {{ ref('stg_tickets') }}
),
decoded AS(
    SELECT id
         , subject
         , group_id
         , requester_id
         , responder_id
         , source
         , status
         , CASE status
            WHEN 2 THEN 'Open'
            WHEN 3 THEN 'Pending'
            WHEN 4 THEN 'Resolved'
            WHEN 5 THEN 'Closed'
          END AS status_label
         , priority
         , CASE priority
            WHEN 1 THEN 'Low'
            WHEN 2 THEN 'Medium'
            WHEN 3 THEN 'High'
            WHEN 4 THEN 'Urgent'
           END AS priority_label
         , company_id
         , type
         , due_by
         , fr_due_by
         , custom_fields:cf_modulo::VARCHAR             AS modulo
         , custom_fields:cf_nivel_de_urgencia::VARCHAR  AS nivel_de_urgencia
         , created_at
         , updated_at
         , nr_due_by
         , _loaded_at
         , _batch_id
      FROM bronze
)
SELECT *
  FROM decoded