-- Desempenho por agente e canal, somente com os registros aproveitados.
WITH resumo AS (
 SELECT equipe,agente,canal,COUNT(*) AS atendimentos,
 SUM(CASE WHEN venda>0 THEN 1 ELSE 0 END) AS vendas,
 SUM(venda) AS receita,SUM(tempo_min) AS minutos,
 AVG(nota_satisfacao) AS satisfacao_media,COUNT(nota_satisfacao) AS notas_validas
 FROM atendimentos_limpos GROUP BY equipe,agente,canal
), metricas AS (
 SELECT *,100.0*vendas/atendimentos AS conversao_pct,
 receita/NULLIF(vendas,0) AS ticket_medio,receita/NULLIF(minutos,0) AS receita_minuto
 FROM resumo WHERE atendimentos>=100
), comparacao AS (
 SELECT *,RANK() OVER(PARTITION BY canal ORDER BY receita_minuto DESC) AS posicao_canal,
 SUM(receita) OVER(PARTITION BY canal)/NULLIF(SUM(minutos) OVER(PARTITION BY canal),0) AS referencia
 FROM metricas
)
SELECT equipe,canal,agente,posicao_canal,atendimentos,vendas,
 ROUND(receita,2) AS receita,ROUND(conversao_pct,2) AS conversao_pct,
 ROUND(ticket_medio,2) AS ticket_medio,ROUND(receita_minuto,2) AS receita_minuto,
 ROUND(100*(receita_minuto/NULLIF(referencia,0)-1),2) AS diferenca_canal_pct,
 ROUND(satisfacao_media,2) AS satisfacao_media,notas_validas
FROM comparacao ORDER BY equipe,canal,posicao_canal,agente;
