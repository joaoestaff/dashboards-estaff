# Queries para demonstrativo de contratos

SQL_CONTRATOS_ENVIADOS = """
#################################################################################################################
# Contratos enviados: CONTRATO_ENVIADO = 1 e CONTRATO_ASSINADO = 0
#################################################################################################################
SELECT
  tc.ID AS ID_COMPANY,
  tc.NAME AS NOME_FANTASIA,
  tcs.ID AS ID_STATUS_CADASTRAL,
  tcs.STATUS AS STATUS_CADASTRAL,
  tc.CORPORATE_NAME as RAZAO_SOCIAL,
  tc.CNPJ,
  tc.CITY AS CIDADE,
  tc.UF AS ESTADO,
  tc.CPF_REPRESENTANTE,
  tc.NOME_REPRESENTANTE,
  tc.EMAIL_REPRESENTANTE,
  tc.PERCENTUAL AS TAXA_ESTAFF,
  tc.CONTRATO_ENVIADO,
  tc.CONTRATO_ASSINADO,
  tc.MAXIMO_CONTRATACOES_SEMANA,
  tc.DATA_CRIACAO,
  tc.DATA_APROVACAO
FROM T_COMPANIES tc
INNER JOIN T_COMPANY_STATUS tcs on tcs.ID = tc.FK_STATUS_CADASTRAL
#WHERE tc.CONTRATO_ENVIADO = 1 AND tc.CONTRATO_ASSINADO = 0
ORDER BY tc.DATA_CRIACAO DESC
"""

SQL_CONTRATOS_PENDENTES = """
#################################################################################################################
# Contratos pendentes de assinatura: CONTRATO_ENVIADO = 1 e CONTRATO_ASSINADO = 0 (mesmo que enviados)
#################################################################################################################
SELECT
  tc.ID AS ID_COMPANY,
  tc.NAME AS NOME_FANTASIA,
  tc.CORPORATE_NAME as RAZAO_SOCIAL,
  tc.CNPJ,
  tc.CITY AS CIDADE,
  tc.UF AS ESTADO,
  tc.CPF_REPRESENTANTE,
  tc.NOME_REPRESENTANTE,
  tc.EMAIL_REPRESENTANTE,
  tc.CONTRATO_ENVIADO,
  tc.CONTRATO_ASSINADO,
  tc.DATA_CRIACAO
FROM T_COMPANIES tc
INNER JOIN T_COMPANY_STATUS tcs on tcs.ID = tc.FK_STATUS_CADASTRAL
WHERE tc.CONTRATO_ENVIADO = 1 AND tc.CONTRATO_ASSINADO = 0
ORDER BY tc.DATA_CRIACAO DESC
"""

SQL_CONTRATOS_ASSINADOS = """
#################################################################################################################
# Contratos assinados: CONTRATO_ASSINADO = 1
#################################################################################################################
SELECT
  tc.ID AS ID_COMPANY,
  tc.NAME AS NOME_FANTASIA,
  tc.CORPORATE_NAME as RAZAO_SOCIAL,
  tc.CNPJ,
  tc.CITY AS CIDADE,
  tc.UF AS ESTADO,
  tc.CPF_REPRESENTANTE,
  tc.NOME_REPRESENTANTE,
  tc.EMAIL_REPRESENTANTE,
  tc.CONTRATO_ENVIADO,
  tc.CONTRATO_ASSINADO,
  tc.DATA_CRIACAO
FROM T_COMPANIES tc
INNER JOIN T_COMPANY_STATUS tcs on tcs.ID = tc.FK_STATUS_CADASTRAL
WHERE tc.CONTRATO_ASSINADO = 1
ORDER BY tc.DATA_APROVACAO DESC
"""