# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 20:15:07 2021

@author: Rodrigo
"""
import requests
import pandas as pd
import re
from datetime import datetime as dt


def corrigindo_valores(df):
    for i in range(len(df)):
        for a in df.columns:
            if(type(df[a][i]) == str):
                df[a][i] = df[a][i].replace(".", "")
                df[a][i] = df[a][i].replace(",", ".")
                df[a][i] = df[a][i].replace("%", "")
                df[a][i] = pd.to_numeric(df[a][i], errors="ignore")


def busca(url):
    header = {
          "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/50.0.2661.75 Safari/537.36",
          "X-Requested-With": "XMLHttpRequest"
        }

    r = requests.get(url, headers=header)
    informacoes = pd.read_html(r.text, decimal=".", thousands=".")
    return(informacoes)


def lista_para_busca():
    empresas_listadas = busca(
        url="https://www.fundamentus.com.br/resultado.php"
        )[0]
    corrigindo_valores(df=empresas_listadas)
    for i in range(len(empresas_listadas["Papel"])):
        if (
            (empresas_listadas["Liq.2meses"][i] < 6000000) or
            (empresas_listadas["P/L"][i] <= 0) or
            (empresas_listadas["Cresc. Rec.5a"][i] <= 0)
        ):
            empresas_listadas = empresas_listadas.drop(i)
    return(empresas_listadas.reset_index(drop=True))


def escolhendo_top20(acoes_pesquisadas):
    a_p = acoes_pesquisadas
    a_p.sort_values(by=["Desconto"], ascending=False, inplace=True)
    a_p = a_p.reset_index(drop=True)

    papel_list = []
    corrigir_papeis_repetidos = []
    for i in range(len(a_p)):
        papel = a_p["Papel"][i]
        papel = re.sub('[0-9]', '', papel)
        papel_list.append(papel)
        if(not papel_list.count(papel) > 1):
            corrigir_papeis_repetidos.append(a_p.iloc[i])

    a_p = pd.DataFrame(corrigir_papeis_repetidos).reset_index(drop=True)

    setores = []
    papeis = []
    limit_number = 15
    for num in range(len(a_p["Setor"])):
        if(limit_number == 0):
            break
        if(setores.count(a_p["Setor"][num]) < 4):
            limit_number -= 1
            setores.append(a_p["Setor"][num])
            papeis.append(a_p.iloc[num])

    carteira = pd.DataFrame(papeis).reset_index(drop=True)

    carteira = pd.DataFrame([carteira["Papel"],
                            carteira["Data últ cot"],
                            carteira["Cotação"],
                            carteira["Desconto"],
                            carteira["Preço justo"],
                            carteira["Div. Yield"],
                            carteira["Setor"]]).transpose()
    nome_xlsx = str("TOP15_" + str(dt.now().date()) + ".xlsx")
    carteira.to_excel(nome_xlsx, index=False)
    return(carteira)


def exibir_na_tela(carteira):
    print("\n\n\n == Ticker ===== Preço ==== Preço Justo ==== Desconto ==\n")
    for i in range(len(carteira)):
        if(carteira["Cotação"][i] < 10):
            cotacao = "0" + str('{:.2f}'.format(carteira["Cotação"][i]))
        else:
            cotacao = str('{:.2f}'.format(carteira["Cotação"][i]))

        if(carteira["Preço justo"][i] < 10):
            p_justo = "0" + str('{:.2f}'.format(carteira["Preço justo"][i]))
        else:
            p_justo = str('{:.2f}'.format(carteira["Preço justo"][i]))

        if(len(carteira["Papel"][i]) == 6):
            print("    ", carteira["Papel"][i], "    ",
                  cotacao, "       ", p_justo, "        ",
                  str(carteira["Desconto"][i])+"%")
        else:
            print("    ", carteira["Papel"][i], "     ",
                  cotacao, "       ", p_justo, "        ",
                  str(carteira["Desconto"][i])+"%")
    input("")
