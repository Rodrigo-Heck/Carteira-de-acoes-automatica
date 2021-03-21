# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 12:24:59 2021

@author: Rodrigo
"""

import os
import pandas as pd
import capturando_tickers as tk
from datetime import datetime as dt
import time

os.system('cls')
print("\n\n\n ===============\n")
print(" Iniciando a Busca!")
print("\n ===============")

base_dados = pd.DataFrame()

busca = tk.lista_para_busca()["Papel"]

contador = 0
for numero_busca in range(len(busca)):

    ticker = busca[numero_busca]
    tentativas_consulta = 0

    while(tentativas_consulta < 3):
        try:
            acao = tk.busca(
                url="https://www.fundamentus.com.br/detalhes.php?papel="
                + ticker
                )
            acao[0] = acao[0].transpose()
            acao[1] = acao[1].transpose()
            acao[2] = ((acao[2].transpose()).drop(columns=[0]))
            acao[3] = ((acao[3].transpose()).drop(columns=[0]))
            acao[4] = ((acao[4].transpose()).drop(columns=[0]))

            filtrando = pd.concat([
                            acao[0].iloc[0:2].reset_index(drop=True),
                            acao[0].iloc[2:4].reset_index(drop=True),
                            acao[1].iloc[0:2].reset_index(drop=True),
                            acao[1].iloc[2:4].reset_index(drop=True),
                            acao[2].iloc[4:6].reset_index(drop=True),
                            acao[2].iloc[2:4].reset_index(drop=True),
                            acao[2].iloc[0:2].reset_index(drop=True),
                            acao[3].iloc[0:2].reset_index(drop=True),
                            acao[3].iloc[2:4].reset_index(drop=True),
                              ], axis=1, join="inner")

            filtrando.columns = filtrando.iloc[0]
            filtrando = filtrando.drop(0)

            novo_cabecario = []
            for i in range(len(filtrando.columns)):
                if(type(filtrando.columns[i]) == str):
                    novo_cabecario.append(
                        filtrando.columns[i].replace('?', '')
                        )
                else:
                    novo_cabecario.append("excluir")

            filtrando.columns = novo_cabecario
            filtrando = filtrando.drop(columns="excluir")
            filtrando = filtrando.reset_index(drop=True)

            # tratando numeros do dataframe
            tk.corrigindo_valores(df=filtrando)

            LPA = float(filtrando["LPA"])
            VPA = float(filtrando["VPA"])

            # Formula de Benjamin Graham
            # Valor Intrínseco = raiz quadrada de (22,5 x LPA x VPA)
            preco_justo = ((22.5 * LPA * VPA) ** (1/2))

            preco_justo = float('{:.2f}'.format(preco_justo))
            preco = float(filtrando["Cotação"])
            desconto = float(
                '{:.2f}' .format(((preco_justo - preco) / preco_justo) * 100)
                )

            list1 = list(filtrando.iloc[0].values)
            list1.append(desconto)
            list1.append(preco_justo)
            list1.append(0)
            list2 = list(filtrando.columns)
            list2.append("Desconto")
            list2.append("Preço justo")
            list2.append("Nota")

            filtrando = pd.DataFrame([list2, list1])
            filtrando.columns = filtrando.iloc[0]
            filtrando = filtrando.drop(0)

            base_dados = base_dados.append(filtrando, sort=False)
            os.system('cls')
            print("\n\n ====================\n")
            print(" Buscando:", ticker)
            print("   == ", round((numero_busca * 100) / len(busca)), "% == ")
            print("\n ====================")

            tentativas_consulta = 3
        except:
            tentativas_consulta += 1
            print("Falha: ", ticker)
            print("Tentativas de consulta: ", tentativas_consulta)
            time.sleep(60)

base_dados = base_dados.reset_index(drop=True)

carteira = tk.escolhendo_top20(acoes_pesquisadas=base_dados)
os.system('cls')
print("\n\n\n =============================================\n")
print(" Busca finalizada!")
print(" As informações também estão disponiveis em um arquivo xlsx")
print(" Nome do arquivo: TOP15_" + str(dt.now().date()) + ".xlsx")
print("\n =============================================\n")
tk.exibir_na_tela(carteira)
print("\n =============================================\n")
