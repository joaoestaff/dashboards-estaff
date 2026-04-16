SQL_PENDENTES = """
WITH ULTIMO_STATUS AS (
    SELECT 
        MAX(tasc.ID) as ID_ASSOCIATIVA,
        tasc.FK_COMPANY as FK_COMPANY
    FROM T_ASSOCIATIVA_STATUS_COMERCIAL tasc 
    GROUP BY tasc.FK_COMPANY
)
SELECT
    tc.ID as "ID_Casa",
    tc.NAME as "Casa",
    "1. Sem atendimento" as "Status_Comercial",
    tc.CORPORATE_NAME as "Razão Social",
    tc.CITY,
    tc.UF,
    tc.CNPJ,
    tc.PHONE as "Telefone",
    tc.WEBSITE,
    tc.ZIPCODE as "CEP",
    tc.ADDRESS as "Endereço",
    tc.DATA_CRIACAO,
    tc.DESCRIPTION as "Descrição",
    tc.LATITUDE,
    tc.LONGITUDE
FROM T_COMPANIES tc
LEFT JOIN ULTIMO_STATUS us ON (tc.ID = us.FK_COMPANY)
LEFT JOIN T_ASSOCIATIVA_STATUS_COMERCIAL tasc ON (us.ID_ASSOCIATIVA = tasc.ID)
WHERE tc.FK_STATUS_CADASTRAL IN (100, 105)
AND tc.NAME IS NOT NULL
AND tc.NAME NOT LIKE "%%teste%%"
-- Só aparece aqui se não tiver nenhum status, ou se o status mais recente for 100/105
AND (us.FK_COMPANY IS NULL OR tasc.FK_STATUS_COMERCIAL IN (100, 105))
-- Garante que NÃO aparece se já estiver em atendimento ou implantação
AND (tasc.FK_STATUS_COMERCIAL NOT IN (101,102,103,104,105,106,107,108) 
     OR tasc.FK_STATUS_COMERCIAL IS NULL)
ORDER BY tc.ID DESC
"""

SQL_ATENDIMENTO = """
with ULTIMO_STATUS as (
SELECT 
MAX(tasc.ID) as ID_ASSOCIATIVA,
tasc.FK_COMPANY as FK_COMPANY
FROM T_ASSOCIATIVA_STATUS_COMERCIAL tasc 
GROUP BY tasc.FK_COMPANY
)
SELECT 
tc.ID as 'ID_Casa',
tc.NAME as 'Casa',
tsc.DESCRICAO as 'Status_Comercial',
tasc2.CREATED_AT as 'Primeira_Mudanca_Status',
tasc2.LAST_UPDATE as 'Ultima_Mudanca_Status',

-- Tempo detalhado legível
CONCAT(
    TIMESTAMPDIFF(DAY, tc.DATA_CRIACAO, tasc2.LAST_UPDATE), 'd ',
    MOD(TIMESTAMPDIFF(HOUR, tc.DATA_CRIACAO, tasc2.LAST_UPDATE), 24), 'h ',
    MOD(TIMESTAMPDIFF(MINUTE, tc.DATA_CRIACAO, tasc2.LAST_UPDATE), 60), 'min'
) as 'SLA_Ultimo_Status',

au.FULL_NAME as 'Usuario_Responsavel',
tc.CNPJ,
tc.PHONE as 'Telefone',
tc.WEBSITE,
tc.ZIPCODE as 'CEP',
tc.ADDRESS as 'Endereço',
tc.DATA_CRIACAO,
tc.DESCRIPTION as 'Descrição',
tc.LATITUDE,
tc.LONGITUDE

from T_COMPANIES tc
LEFT JOIN ULTIMO_STATUS us ON (tc.ID = us.FK_COMPANY)
LEFT JOIN T_ASSOCIATIVA_STATUS_COMERCIAL tasc2 on (us.ID_ASSOCIATIVA = tasc2.ID)
LEFT JOIN T_STATUS_COMERCIAL tsc ON (tasc2.FK_STATUS_COMERCIAL = tsc.ID)
LEFT JOIN ADMIN_USERS au ON (tasc2.FIRST_USER = au.ID)
WHERE us.FK_COMPANY IS NOT NULL
AND tasc2.FK_STATUS_COMERCIAL in (101,102,103,104)
order by tc.ID desc
"""

SQL_IMPLANTACAO = """
WITH ULTIMO_STATUS AS (
    SELECT
        MAX(tasc.ID) AS ID_ASSOCIATIVA,
        tasc.FK_COMPANY
    FROM T_ASSOCIATIVA_STATUS_COMERCIAL tasc
    GROUP BY tasc.FK_COMPANY
)
SELECT
    tc.ID                          AS ID_Casa,
    tc.NAME                        AS Casa,
    tsc.DESCRICAO                  AS Status_Comercial,
    tasc2.CREATED_AT               AS Data_Mudanca_Status,
    au.FULL_NAME                   AS Usuario_Responsavel,
    tc.CNPJ,
    tc.PHONE                       AS Telefone,
    tc.WEBSITE,
    tc.ZIPCODE                     AS CEP,
    tc.ADDRESS                     AS Endereço,
    tc.DATA_CRIACAO,
    tc.DESCRIPTION                 AS Descrição,
    tc.LATITUDE,
    tc.LONGITUDE
FROM T_COMPANIES tc
LEFT JOIN ULTIMO_STATUS us           ON (tc.ID = us.FK_COMPANY)
LEFT JOIN T_ASSOCIATIVA_STATUS_COMERCIAL tasc2 ON (us.ID_ASSOCIATIVA = tasc2.ID)
LEFT JOIN T_STATUS_COMERCIAL tsc     ON (tasc2.FK_STATUS_COMERCIAL = tsc.ID)
LEFT JOIN ADMIN_USERS au             ON (tasc2.FIRST_USER = au.ID)
WHERE us.FK_COMPANY IS NOT NULL
  AND tasc2.FK_STATUS_COMERCIAL IN (105, 106, 107, 108)
ORDER BY tc.ID DESC
"""

SQL_CHURNS = """
WITH filtered AS (
  SELECT
    TC.ID        AS company_id,
    TC.NAME      AS company_name,
    TO2.START_AT AS start_at
  FROM T_PROPOSALS TP 
  INNER JOIN T_PROPOSAL_STATUS   TPS ON TP.FK_PROPOSAL_STATUS = TPS.ID
  INNER JOIN T_FREELA            TF  ON TP.FK_FREELA          = TF.ID
  INNER JOIN ADMIN_USERS         AU  ON TF.FK_ADMIN_USERS     = AU.ID
  INNER JOIN T_OPPORTUNITIES     TO2 ON TP.FK_OPPORTUNITIE    = TO2.ID
  INNER JOIN T_COMPANIES         TC  ON TO2.FK_COMPANIE       = TC.ID
  INNER JOIN T_PROPOSAL_TYPE     TPT ON TO2.FK_PROPOSAL_TYPE  = TPT.ID
  LEFT  JOIN T_STATUS_PAGAMENTO  TSP ON TP.FK_STATUS_PAGAMENTO = TSP.ID
  LEFT  JOIN T_COMPANY_GROUP     TCG ON TC.FK_GROUP           = TCG.ID
  WHERE TP.FK_PROPOSAL_STATUS IN (102,103,106,115)
    AND TC.ID <> 111
    AND (TC.FK_GROUP IS NULL OR TC.FK_GROUP <> 113)
),

last_op AS (
  SELECT 
    company_id, 
    MIN(start_at) AS first_start,
    MAX(start_at) AS last_start
  FROM filtered
  GROUP BY company_id
),

last_op_in_range AS (
  SELECT company_id, first_start, last_start
  FROM last_op
  WHERE last_start >= '2025-10-01'
    AND last_start < DATE_FORMAT(CURDATE(), '%%Y-%%m-01')
)

SELECT
  lo.company_id,
  tc.NAME AS Cliente,
  lo.first_start AS Primeira_OP,
  lo.last_start  AS Ultima_OP,
  DATE_FORMAT(lo.last_start, '%%Y-%%m') AS Ano_Mes,

  DATEDIFF(CURDATE(), lo.last_start) AS Dias_Sem_OP,

  CASE
    WHEN DATEDIFF(CURDATE(), lo.last_start) <= 30 THEN 'Ativo'
    WHEN DATEDIFF(CURDATE(), lo.last_start) BETWEEN 31 AND 90 THEN 'Em Risco'
    ELSE 'Churn'
  END AS Status_Cliente

FROM last_op_in_range lo
JOIN T_COMPANIES tc ON tc.ID = lo.company_id
ORDER BY Ano_Mes DESC, tc.NAME;
"""

SQL_CHURNS = """
WITH filtered AS (
  SELECT
    TC.ID        AS company_id,
    TC.NAME      AS company_name,
    TO2.START_AT AS start_at
  FROM T_PROPOSALS TP 
  INNER JOIN T_PROPOSAL_STATUS   TPS ON TP.FK_PROPOSAL_STATUS = TPS.ID
  INNER JOIN T_FREELA            TF  ON TP.FK_FREELA          = TF.ID
  INNER JOIN ADMIN_USERS         AU  ON TF.FK_ADMIN_USERS     = AU.ID
  INNER JOIN T_OPPORTUNITIES     TO2 ON TP.FK_OPPORTUNITIE    = TO2.ID
  INNER JOIN T_COMPANIES         TC  ON TO2.FK_COMPANIE       = TC.ID
  INNER JOIN T_PROPOSAL_TYPE     TPT ON TO2.FK_PROPOSAL_TYPE  = TPT.ID
  LEFT  JOIN T_STATUS_PAGAMENTO  TSP ON TP.FK_STATUS_PAGAMENTO = TSP.ID
  LEFT  JOIN T_COMPANY_GROUP     TCG ON TC.FK_GROUP           = TCG.ID
  WHERE TP.FK_PROPOSAL_STATUS IN (102,103,106,115)
    AND TC.ID <> 111
    AND (TC.FK_GROUP IS NULL OR TC.FK_GROUP <> 113)
),

last_op AS (
  SELECT 
    company_id, 
    MIN(start_at) AS first_start,
    MAX(start_at) AS last_start
  FROM filtered
  GROUP BY company_id
),

last_op_in_range AS (
  SELECT company_id, first_start, last_start
  FROM last_op
  WHERE last_start >= '2025-10-01'
    AND last_start < DATE_FORMAT(CURDATE(), '%%Y-%%m-01')
)

SELECT
  lo.company_id,
  tc.NAME AS Cliente,
  lo.first_start AS Primeira_OP,
  lo.last_start  AS Ultima_OP,
  DATE_FORMAT(lo.last_start, '%%Y-%%m') AS Ano_Mes,

  DATEDIFF(CURDATE(), lo.last_start) AS Dias_Sem_OP,

  CASE
    WHEN DATEDIFF(CURDATE(), lo.last_start) <= 30 THEN 'Ativo'
    WHEN DATEDIFF(CURDATE(), lo.last_start) BETWEEN 31 AND 90 THEN 'Em Risco'
    ELSE 'Churn'
  END AS Status_Cliente

FROM last_op_in_range lo
JOIN T_COMPANIES tc ON tc.ID = lo.company_id
ORDER BY Ano_Mes DESC, tc.NAME;
"""
