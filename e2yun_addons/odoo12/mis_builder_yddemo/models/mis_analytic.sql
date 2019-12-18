CREATE OR REPLACE VIEW mis_analytic AS (
    SELECT ROW_NUMBER() OVER() AS id, mis_analytic.* FROM (

        WITH currency_rate as (
            SELECT
              r.currency_id,
              COALESCE(r.company_id, c.id) as company_id,
              r.rate,
              r.name AS date_start,
              (SELECT name FROM res_currency_rate r2
              WHERE r2.name > r.name AND
                    r2.currency_id = r.currency_id AND
                    (r2.company_id is null or r2.company_id = c.id)
               ORDER BY r2.name ASC
               LIMIT 1) AS date_end
            FROM res_currency_rate r
              JOIN res_company c ON (r.company_id is null or r.company_id = c.id)
        )

        /*  Analytic */
    SELECT
        'account analytic' AS line_type,
                aal.company_id AS company_id,
        aal.name AS name,
        aal.date as date,
        aal.account_id as analytic_account_id,
        aal.id AS res_id,
        'account.analytic.line' AS res_model,
        aa.id AS account_id,
        CASE
          WHEN (aal.amount)::decimal(16,2) >= 0.0 THEN aal.amount
          ELSE 0.0
        END AS debit,
        CASE
          WHEN (aal.amount)::decimal(16,2) < 0 THEN aal.amount * -1
          ELSE 0.0
        END AS credit
        FROM account_analytic_line aal
            LEFT JOIN account_analytic_account aa on aa.id = aal.account_id
            LEFT JOIN currency_rate cur on (cur.currency_id = aal.currency_id and
                cur.company_id = aal.company_id and
                cur.date_start <= coalesce(aal.date, now()) and
                (cur.date_end is null or cur.date_end > coalesce(aal.date, now())))



    ) AS mis_analytic
)