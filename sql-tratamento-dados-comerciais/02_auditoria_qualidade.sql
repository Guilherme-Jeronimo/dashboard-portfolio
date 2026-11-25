-- Execute depois de 01_preparacao.sql. Contagens de rejeicao usam o primeiro motivo.
SELECT '01 - Linhas recebidas' AS indicador,COUNT(*) AS quantidade FROM atendimentos_brutos
UNION ALL SELECT '02 - Versoes repetidas removidas',
 (SELECT COUNT(*) FROM atendimentos_brutos)-(SELECT COUNT(*) FROM atendimentos_deduplicados)
UNION ALL SELECT '03 - Atendimentos unicos',COUNT(*) FROM atendimentos_deduplicados
UNION ALL SELECT '04 - Atendimentos rejeitados',COUNT(*) FROM registros_rejeitados
UNION ALL SELECT '05 - Atendimentos aproveitados',COUNT(*) FROM atendimentos_limpos
UNION ALL SELECT '06 - Notas ausentes/invalidas na base limpa',COUNT(*) FROM atendimentos_limpos WHERE nota_satisfacao IS NULL
UNION ALL SELECT 'Rejeicao: '||motivo_rejeicao,COUNT(*) FROM registros_rejeitados GROUP BY motivo_rejeicao;
