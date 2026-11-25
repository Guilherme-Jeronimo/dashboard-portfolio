-- Mes anterior observado. Nesta base ha movimento em todos os meses por equipe.
WITH mensal AS (
 SELECT equipe,STRFTIME('%Y-%m',data_hora) AS mes,
 COUNT(*) AS atendimentos,SUM(venda) AS receita
 FROM atendimentos_limpos GROUP BY equipe,STRFTIME('%Y-%m',data_hora)
), historico AS (
 SELECT *,LAG(receita) OVER(PARTITION BY equipe ORDER BY mes) AS receita_anterior,
 SUM(receita) OVER(PARTITION BY equipe ORDER BY mes ROWS UNBOUNDED PRECEDING) AS acumulado,
 AVG(receita) OVER(PARTITION BY equipe ORDER BY mes ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS media_movel
 FROM mensal
)
SELECT equipe,mes,atendimentos,ROUND(receita,2) AS receita,
 ROUND(receita_anterior,2) AS receita_anterior,
 ROUND(100*(receita-receita_anterior)/NULLIF(receita_anterior,0),2) AS variacao_pct,
 ROUND(acumulado,2) AS receita_acumulada,ROUND(media_movel,2) AS media_movel_ate_3_meses
FROM historico ORDER BY equipe,mes;
