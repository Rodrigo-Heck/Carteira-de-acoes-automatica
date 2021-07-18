# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 20:15:07 2021

@author: Rodrigo
"""
import requests
import pandas as pd
import re
from selenium import webdriver


def corrigindo_valores(df):
    for i in range(len(df)):
        for a in df.columns:
            if(type(df[a][i]) == str):
                df[a][i] = df[a][i].replace(".", "")
                df[a][i] = df[a][i].replace(",", ".")
                df[a][i] = df[a][i].replace("%", "")
                df[a][i] = pd.to_numeric(df[a][i], errors="ignore")


def buscar(url):
    header = {
          "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/50.0.2661.75 Safari/537.36",
          "X-Requested-With": "XMLHttpRequest"
        }

    r = requests.get(url, headers=header)
    informacoes = pd.read_html(r.text, decimal=".", thousands=".")
    return(informacoes)


def busca_filtrada():
    empresas_listadas = buscar(
        url="https://www.fundamentus.com.br/resultado.php"
        )[0]
    corrigindo_valores(df=empresas_listadas)
    for i in range(len(empresas_listadas["Papel"])):
        if (
            (empresas_listadas["Liq.2meses"][i] < 200000) or
            (empresas_listadas["EV/EBIT"][i] <= 0)

        ):
            empresas_listadas = empresas_listadas.drop(i)
    return(empresas_listadas.reset_index(drop=True))


def remover_papeis_repetidos(fundamentus):
    papel_list = []
    papeis_repetidos = []

    for i in range(len(fundamentus)):
        papel = fundamentus["Papel"][i]
        papel = re.sub('[0-9]', '', papel)
        papel_list.append(papel)

        if((papel_list.count(papel) > 1) and (papel not in papeis_repetidos)):
            papeis_repetidos.append(papel)

    fundamentus.index = fundamentus["Papel"]

    maior_liquidez = []

    for ticker in papeis_repetidos:

        escolher_papel = []
        liquidez = []
        for i in range(len(fundamentus)):
            if(re.sub('[0-9]', '', fundamentus["Papel"][i]) == ticker):

                escolher_papel.append(fundamentus["Papel"][i])
                liquidez.append(
                    fundamentus.loc[fundamentus["Papel"][i]]["Liq.2meses"]
                    )

        escolher_papel.remove(escolher_papel[liquidez.index(max(liquidez))])

        for i in escolher_papel:
            fundamentus = fundamentus.drop(fundamentus.loc[i]["Papel"])
    return(fundamentus.reset_index(drop=True))


def remover_seguradoras_e_rj(fundamentus):
    comprar = []
    navegador = webdriver.Chrome()
    contador = 0

    for i in range(len(fundamentus["Papel"])):
        ticker = fundamentus["Papel"][i]

        navegador.get("https://statusinvest.com.br/acoes/" + ticker)

        info = navegador.find_element_by_xpath(
            '//*[@id="company-section"]/div/div[1]/div[2]'
            ).text

        segmento = navegador.find_element_by_xpath(
         '//*[@id="company-section"]/div/div[3]/div/div[3]/div/div/div/a/strong'
            ).text

        if(("RECUPERAÇÃO JUDICIAL" in info) or ("Seguradoras" in segmento)):
            print("nao comprar: ")
        else:
            contador += 1
            comprar.append(ticker)

        if(contador >= 20):
            print("===========================")
            return(comprar)


