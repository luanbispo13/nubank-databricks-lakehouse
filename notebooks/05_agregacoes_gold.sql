-- Databricks notebook source
USE CATALOG nubank_lakehouse;

-- Tabela 1: Evolução mensal de gastos por categoria
CREATE OR REPLACE TABLE gold.gastos_mensais_categoria AS
SELECT 
    DATE_TRUNC('month', data_transacao) AS mes_referencia,
    categoria,
    COUNT(*) AS qtd_compras,
    SUM(valor) AS total_gasto,
    ROUND(AVG(valor), 2) AS ticket_medio
FROM silver.transacoes_limpas
WHERE tipo_movimentacao = 'Compra'
GROUP BY 1, 2
ORDER BY 1 ASC, 4 DESC;

-- Tabela 2: Ranking de estabelecimentos onde mais se gasta
CREATE OR REPLACE TABLE gold.ranking_estabelecimentos AS
SELECT 
    estabelecimento_limpo,
    categoria,
    COUNT(*) AS frequencia_compras,
    SUM(valor) AS valor_total_gasto,
    ROUND(AVG(valor), 2) AS ticket_medio,
    MAX(data_transacao) AS data_ultima_compra
FROM silver.transacoes_limpas
WHERE tipo_movimentacao = 'Compra'
GROUP BY 1, 2
ORDER BY valor_total_gasto DESC;

-- Tabela 3: Proporção de compras à vista vs. parceladas por mês
CREATE OR REPLACE TABLE gold.analise_parcelamentos AS
SELECT 
    DATE_TRUNC('month', data_transacao) AS mes_referencia,
    CASE WHEN is_parcelado THEN 'Parcelado' ELSE 'À Vista' END AS modalidade,
    COUNT(*) AS qtd_transacoes,
    SUM(valor) AS total_gasto
FROM silver.transacoes_limpas
WHERE tipo_movimentacao = 'Compra'
GROUP BY 1, 2
ORDER BY 1 ASC;