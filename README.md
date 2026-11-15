# 💳 Nubank Credit Card Lakehouse — Engenharia de Dados no Databricks

Pipeline completo de Engenharia de Dados construído no **Databricks** utilizando **Arquitetura Medalhão**, **Delta Lake**, **Unity Catalog**, **PySpark**, **SQL** e **Databricks Workflows** para ingestão, tratamento, governança e análise de gastos de faturas de cartão de crédito.

---

## 🏗️ Arquitetura da Solução

O projeto implementa um fluxo ponta a ponta dentro do catálogo `nubank_lakehouse` no Unity Catalog:

1. **Geração de Dados & Landing Zone (`/Volumes/nubank_lakehouse/bronze/raw_files`):**
   * Script em Python gerando 12 meses de faturas mensais em CSV no padrão exportado pelo Nubank, incluindo anomalias propositais (duplicidades, valores nulos, prefixos de adquirentes como `IFD*`, `PAG*`, `MP *`, estornos e compras parceladas).
2. **Camada Bronze (`nubank_lakehouse.bronze.fatura_cartao_raw`):**
   * Ingestão bruta via PySpark em formato **Delta Lake**, mantendo a tipagem original (`STRING`) para resiliência contra falhas de schema e adicionando colunas de auditoria (`_ingestion_timestamp` e `_source_file`).
3. **Camada Silver (`nubank_lakehouse.silver.transacoes_limpas`):**
   * Limpeza e padronização com PySpark: conversão de tipos (`DATE` e `DECIMAL(10,2)`), remoção de registros corrompidos e duplicatas, limpeza de nomes de estabelecimentos via **Regex**, identificação de compras parceladas e classificação de lançamentos (`Compra`, `Estorno` e `Pagamento Fatura`).
4. **Camada Gold (`nubank_lakehouse.gold.*`):**
   * Modelagem analítica em **SQL** gerando tabelas certificadas para consumo direto em dashboards de BI:
     * `gastos_mensais_categoria`: Evolução mensal de gastos, volume de compras e ticket médio por categoria.
     * `ranking_estabelecimentos`: Frequência de compras, valor acumulado e última compra por estabelecimento.
     * `analise_parcelamentos`: Comparativo mensal entre compras à vista e parceladas.
5. **Orquestração & BI:**
   * Pipeline automatizado via **Databricks Workflows** (`pipeline_fatura_nubank`) encadeando as tarefas `Bronze -> Silver -> Gold` e alimentando um painel no **Databricks AI/BI Dashboards**.

---

## 🔍 Linhagem de Dados e Governança (Unity Catalog)

A rastreabilidade em nível de tabela e coluna foi capturada nativamente pelo **Unity Catalog**, demonstrando a derivação desde a camada Silver até os ativos de leitura da camada Gold, além da aplicação de **System Tags (Certificação de Dados)** para homologação das tabelas analíticas:

![Data Lineage - Unity Catalog](images/data_lineage.png)

---

## 🛠️ Tecnologias Utilizadas

* **Plataforma:** Databricks (Serverless Compute)
* **Governança & Catálogo:** Unity Catalog (Volumes, Schemas, Data Lineage e Certificação)
* **Armazenamento:** Delta Lake
* **Processamento & Transformação:** Python (PySpark, Pandas, NumPy) e Spark SQL
* **Orquestração:** Databricks Workflows (Jobs)
* **Visualização:** Databricks AI/BI Dashboards

---

## 📂 Estrutura do Repositório

```text
├── images/
│   └── data_lineage.png              # Grafo de linhagem de dados no Unity Catalog
├── notebooks/
│   ├── 01_setup_unity_catalog.sql    # Criação do catálogo, schemas e volume gerenciado
│   ├── 02_gerar_dados_sinteticos.py  # Gerador de 12 faturas mensais em CSV com sujeiras propositais
│   ├── 03_ingestao_bronze.py         # Leitura dos CSVs e escrita Delta na camada Bronze
│   ├── 04_tratamento_silver.py       # Deduplicação, tipagem, Regex e regras de negócio na Silver
│   └── 05_agregacoes_gold.sql        # Criação das tabelas analíticas na camada Gold
└── README.md