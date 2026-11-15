-- Databricks notebook source
-- Cria o Catálogo principal do projeto
CREATE CATALOG IF NOT EXISTS nubank_lakehouse;
USE CATALOG nubank_lakehouse;

-- Cria os 3 schemas da Arquitetura Medalhão
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Cria o Volume (pasta gerenciada) para armazenar os CSVs brutos
CREATE VOLUME IF NOT EXISTS bronze.raw_files;