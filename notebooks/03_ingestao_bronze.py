# Databricks notebook source
from pyspark.sql import functions as F

raw_path = "/Volumes/nubank_lakehouse/bronze/raw_files/*.csv"

# Lê todos os CSVs mantendo tudo como STRING (evita falha de ingestão por sujeira nos dados)
df_raw = (
    spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "false")
    .load(raw_path)
)

# Adiciona colunas de auditoria
df_bronze = (
    df_raw
    .withColumn("_ingestion_timestamp", F.current_timestamp())
    .withColumn("_source_file", F.col("_metadata.file_path"))
)

# Salva como tabela Delta gerenciada no Unity Catalog
(
    df_bronze.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("nubank_lakehouse.bronze.fatura_cartao_raw")
)

print(f"Total de linhas ingeridas na Bronze: {spark.table('nubank_lakehouse.bronze.fatura_cartao_raw').count()}")