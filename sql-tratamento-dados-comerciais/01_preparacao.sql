-- SQLite. Execute apos importar atendimentos_brutos.csv como atendimentos_brutos.
-- Nao modifica o CSV: cria views reproduziveis. Reexecutavel.
DROP VIEW IF EXISTS atendimentos_limpos;
DROP VIEW IF EXISTS registros_rejeitados;
DROP VIEW IF EXISTS qualidade_atendimentos;
DROP VIEW IF EXISTS atendimentos_classificados;
DROP VIEW IF EXISTS atendimentos_normalizados;
DROP VIEW IF EXISTS atendimentos_deduplicados;
DROP VIEW IF EXISTS cadastro_agentes;
CREATE VIEW cadastro_agentes AS SELECT 'Ana' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Bruno' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Carla' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Diego' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Eduarda' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Felipe' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Gabriela' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Henrique' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Isabela' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Joao' AS agente, 'Equipe A' AS equipe UNION ALL SELECT 'Karen' AS agente, 'Equipe B' AS equipe UNION ALL SELECT 'Lucas' AS agente, 'Equipe B' AS equipe UNION ALL SELECT 'Mariana' AS agente, 'Equipe B' AS equipe UNION ALL SELECT 'Nicolas' AS agente, 'Equipe B' AS equipe UNION ALL SELECT 'Olivia' AS agente, 'Equipe B' AS equipe UNION ALL SELECT 'Paulo' AS agente, 'Equipe B' AS equipe UNION ALL SELECT 'Renata' AS agente, 'Equipe B' AS equipe UNION ALL SELECT 'Samuel' AS agente, 'Equipe B' AS equipe UNION ALL SELECT 'Tatiana' AS agente, 'Equipe B' AS equipe UNION ALL SELECT 'Victor' AS agente, 'Equipe B' AS equipe;

-- id_registro_origem desempata reexportacoes com o mesmo timestamp.
CREATE VIEW atendimentos_deduplicados AS
SELECT * FROM (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY TRIM(id_atendimento)
 ORDER BY atualizado_em DESC,CAST(id_registro_origem AS INTEGER) DESC) AS ordem_versao
 FROM atendimentos_brutos
) WHERE ordem_versao=1;

CREATE VIEW atendimentos_normalizados AS
SELECT d.id_registro_origem,TRIM(d.id_atendimento) AS id_atendimento,
 TRIM(d.data_hora) AS data_hora,a.agente,a.equipe,
 NULLIF(TRIM(d.id_cliente),'') AS id_cliente,
 CASE UPPER(TRIM(d.canal)) WHEN 'TEL' THEN 'Telefone'
 WHEN 'TELEFONE' THEN 'Telefone' WHEN 'CHAT' THEN 'Chat'
 WHEN 'WHATSAPP' THEN 'WhatsApp' END AS canal,
 CASE UPPER(TRIM(d.produto)) WHEN 'ESSENCIAL' THEN 'Essencial'
 WHEN 'PLUS' THEN 'Plus' WHEN 'PREMIUM' THEN 'Premium' END AS produto,
 REPLACE(REPLACE(REPLACE(TRIM(d.venda),'R$',''),' ',''),',','.') AS venda_texto,
 REPLACE(TRIM(d.tempo_min),',','.') AS tempo_texto,
 TRIM(d.nota_satisfacao) AS nota_texto
FROM atendimentos_deduplicados d
LEFT JOIN cadastro_agentes a ON UPPER(TRIM(d.agente))=UPPER(a.agente);

-- Validacao de numeros ANTES do CAST: SQLite pode converter abc em zero.
-- Formatos aceitos: sinal negativo opcional, digitos, ate um ponto decimal.
CREATE VIEW atendimentos_classificados AS
SELECT *,
 CASE WHEN id_atendimento='' THEN 'ID ausente'
 WHEN agente IS NULL THEN 'Agente ausente ou desconhecido'
 WHEN canal IS NULL THEN 'Canal desconhecido'
 WHEN produto IS NULL THEN 'Produto desconhecido'
 WHEN LENGTH(data_hora)<>19
 OR STRFTIME('%Y-%m-%d %H:%M:%S',JULIANDAY(data_hora)) IS NOT data_hora
 OR SUBSTR(data_hora,1,4)<>'2025' THEN 'Data invalida ou fora do periodo'
 WHEN venda_texto='' OR venda_texto GLOB '*[^0-9.-]*'
 OR (LENGTH(venda_texto)-LENGTH(REPLACE(venda_texto,'.','')))>1
 OR INSTR(SUBSTR(venda_texto,2),'-')>0
 OR venda_texto NOT GLOB '*[0-9]*' THEN 'Venda ausente ou nao numerica'
 WHEN CAST(venda_texto AS REAL)<0 THEN 'Venda negativa'
 WHEN tempo_texto='' OR tempo_texto GLOB '*[^0-9.-]*'
 OR (LENGTH(tempo_texto)-LENGTH(REPLACE(tempo_texto,'.','')))>1
 OR INSTR(SUBSTR(tempo_texto,2),'-')>0
 OR tempo_texto NOT GLOB '*[0-9]*' THEN 'Duracao ausente ou nao numerica'
 WHEN CAST(tempo_texto AS REAL)<=0 THEN 'Duracao nao positiva'
 END AS motivo_rejeicao
FROM atendimentos_normalizados;

CREATE VIEW registros_rejeitados AS
SELECT * FROM atendimentos_classificados WHERE motivo_rejeicao IS NOT NULL;

CREATE VIEW atendimentos_limpos AS
SELECT CAST(id_atendimento AS INTEGER) AS id_atendimento,data_hora,
 agente,equipe,id_cliente,canal,produto,
 CAST(venda_texto AS REAL) AS venda,CAST(tempo_texto AS REAL) AS tempo_min,
 CASE WHEN nota_texto IN ('1','2','3','4','5')
 THEN CAST(nota_texto AS INTEGER) END AS nota_satisfacao
FROM atendimentos_classificados WHERE motivo_rejeicao IS NULL;
