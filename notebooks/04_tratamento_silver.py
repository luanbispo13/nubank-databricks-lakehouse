# Databricks notebook source
from pyspark.sql import functions as F

df_bronze = spark.read.table("nubank_lakehouse.bronze.fatura_cartao_raw")

df_silver = (
    df_bronze
    # 1. Conversão de tipos (String -> Date e Decimal)
    .withColumn("data_transacao", F.to_date(F.col("date"), "yyyy-MM-dd"))
    .withColumn("valor", F.col("amount").cast("decimal(10,2)"))
    
    # 2. Remove linhas corrompidas (onde data ou valor são nulos)
    .filter(F.col("data_transacao").isNotNull() & F.col("valor").isNotNull())
    
    # 3. Remove duplicatas exatas
    .dropDuplicates(["data_transacao", "title", "valor"])
    
    # 4. Padroniza nome do estabelecimento (remove prefixos IFD*, PAG*, MP *, * e sufixo de parcela)
    .withColumn(
        "estabelecimento_limpo",
        F.upper(F.trim(
            F.regexp_replace(
                F.regexp_replace(F.col("title"), r"^(IFD\*|PAG\*|MP \*|\*)", ""),
                r"\s*-\s*Parcela\s*\d+/\d+", ""
            )
        ))
    )
    
    # 5. Classifica o tipo de lançamento
    .withColumn(
        "tipo_movimentacao",
        F.when(F.col("title") == "Pagamento recebido", "Pagamento Fatura")
         .when(F.col("valor") < 0, "Estorno")
         .otherwise("Compra")
    )
    
    # 6. Flag de compra parcelada e preenchimento de categoria nula
    .withColumn("is_parcelado", F.col("title").rlike(r"Parcela \d+/\d+"))
    .withColumn("categoria", F.coalesce(F.col("category"), F.lit("outros")))
    
    # 7. Seleciona e organiza as colunas finais
    .select(
        "data_transacao",
        "estabelecimento_limpo",
        "categoria",
        "valor",
        "tipo_movimentacao",
        "is_parcelado",
        "_ingestion_timestamp"
    )
)

(
    df_silver.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("nubank_lakehouse.silver.transacoes_limpas")
)

print(f"Total de linhas válidas na Silver: {spark.table('nubank_lakehouse.silver.transacoes_limpas').count()}")