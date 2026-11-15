# Databricks notebook source
import pandas as pd
import numpy as np
import random
import os

random.seed(42)
np.random.seed(42)

output_dir = "/Volumes/nubank_lakehouse/bronze/raw_files"
os.makedirs(output_dir, exist_ok=True)

estabelecimentos = [
    ("IFD*IFOOD.COM", "restaurante", (25.0, 120.0)),
    ("IFD*BURGER KING", "restaurante", (30.0, 75.0)),
    ("OUTBACK STEAKHOUSE", "restaurante", (110.0, 280.0)),
    ("PADARIA PAO DOURADO", "restaurante", (12.0, 45.0)),
    ("UBER *TRIP", "transporte", (11.0, 55.0)),
    ("99APP *99POP", "transporte", (10.0, 48.0)),
    ("POSTO SHELL IPIRANGA", "transporte", (100.0, 260.0)),
    ("CARREFOUR Hiper", "supermercado", (150.0, 650.0)),
    ("PAO DE ACUCAR", "supermercado", (80.0, 350.0)),
    ("PAG*MercadinhoBairro", "supermercado", (20.0, 90.0)),
    ("NETFLIX.COM", "servicos", (39.90, 55.90)),
    ("SPOTIFY P39482", "servicos", (21.90, 34.90)),
    ("AMAZON PRIME BR", "servicos", (19.90, 19.90)),
    ("DROGASIL 1422", "saude", (35.0, 190.0)),
    ("DROGARIA SAO PAULO", "saude", (25.0, 140.0)),
    ("SMART FIT ACADEMIA", "saude", (119.90, 139.90)),
    ("AMAZON.COM.BR", "eletronicos", (60.0, 800.0)),
    ("MP *MERCADOLIVRE", "eletronicos", (45.0, 600.0)),
    ("KABUM! E-COMMERCE", "eletronicos", (150.0, 1500.0)),
    ("ZARA BRASIL", "vestuario", (120.0, 450.0)),
    ("LOJAS RENNER", "vestuario", (80.0, 320.0)),
    ("CINEMARK BRASIL", "lazer", (40.0, 110.0)),
    ("SYMPLA *INGRESSOS", "lazer", (60.0, 250.0))
]

meses = pd.date_range(start="2025-11-01", end="2026-10-01", freq="MS")
total_registros = 0

for mes_inicio in meses:
    dados_mes = []
    dias_no_mes = (mes_inicio + pd.offsets.MonthEnd(1)).day
    qtd_transacoes = random.randint(120, 180)
    
    for _ in range(qtd_transacoes):
        dia = random.randint(1, dias_no_mes)
        data_tx = mes_inicio.replace(day=dia).strftime("%Y-%m-%d")
        titulo, categoria, (val_min, val_max) = random.choice(estabelecimentos)
        valor = round(random.uniform(val_min, val_max), 2)
        
        if valor > 200 and categoria in ["eletronicos", "vestuario"] and random.random() < 0.45:
            total_parcelas = random.choice([2, 3, 5, 6, 10])
            parcela_atual = random.randint(1, total_parcelas)
            valor = round(valor / total_parcelas, 2)
            titulo = f"{titulo} - Parcela {parcela_atual}/{total_parcelas}"
            
        dados_mes.append({
            "date": data_tx,
            "category": categoria,
            "title": titulo,
            "amount": valor
        })
    
    # Pagamento da fatura anterior
    dados_mes.append({
        "date": mes_inicio.replace(day=random.randint(5, 10)).strftime("%Y-%m-%d"),
        "category": "pagamento",
        "title": "Pagamento recebido",
        "amount": round(-random.uniform(1500.0, 4500.0), 2)
    })
    
    # Estorno ocasional
    if random.random() < 0.5:
        estorno_ref = random.choice(estabelecimentos)
        dados_mes.append({
            "date": mes_inicio.replace(day=random.randint(12, 25)).strftime("%Y-%m-%d"),
            "category": estorno_ref[1],
            "title": f"Estorno {estorno_ref[0]}",
            "amount": round(-random.uniform(20.0, 150.0), 2)
        })

    df_mes = pd.DataFrame(dados_mes)
    
    # Sujeiras propositais para a camada Silver limpar
    duplicadas = df_mes.sample(n=3, random_state=42)
    df_mes = pd.concat([df_mes, duplicadas], ignore_index=True)
    idx_nulos = df_mes.sample(frac=0.05, random_state=42).index
    df_mes.loc[idx_nulos, "category"] = np.nan
    df_mes.loc[len(df_mes)] = [mes_inicio.strftime("%Y-%m-%d"), "outros", "ERRO_SISTEMA_TX", np.nan]
    
    df_mes = df_mes.sample(frac=1, random_state=42).reset_index(drop=True)
    
    nome_arquivo = f"nubank_fatura_{mes_inicio.strftime('%Y_%m')}.csv"
    df_mes.to_csv(os.path.join(output_dir, nome_arquivo), index=False)
    total_registros += len(df_mes)

print(f"Concluído! 12 faturas geradas com {total_registros} registros.")