SQL_LTV = """
SELECT
             SUM(P.VALOR_FREELA * (
               CASE WHEN C.PERCENTUAL IS NULL THEN 0
                    WHEN C.PERCENTUAL > 1 THEN C.PERCENTUAL / 100
                    ELSE C.PERCENTUAL END
             )) as ltv,
             C.ID,
             C.NAME,
             TIMESTAMPDIFF(MONTH, MIN(P.CHECKIN), MAX(P.CHECKIN)) as lifespanMonths
            FROM T_PROPOSALS P
            JOIN T_OPPORTUNITIES O ON O.ID = P.FK_OPPORTUNITIE
            JOIN T_COMPANIES C ON C.ID = O.FK_COMPANIE
            WHERE P.FK_PROPOSAL_STATUS IN (101,102,103,106)
              AND P.VALOR_FREELA > 0
              AND (COALESCE(P.CHECKIN, P.DATA_CANDIDATURA_FREELA, P.DATA_CANDIDATURA, P.CREATED_AT, P.LAST_UPDATE) >= DATE_ADD('2026-01-01', INTERVAL 1 DAY))
            GROUP BY O.FK_COMPANIE
           HAVING ltv > 0
"""