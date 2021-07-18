# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 12:24:59 2021

@author: Rodrigo
"""

import re
import pandas as pd
import capturando_tickers as tk


fundamentus = tk.busca_filtrada()

fundamentus = tk.remover_papeis_repetidos(fundamentus)

fundamentus = fundamentus.sort_values(by="EV/EBIT").reset_index(drop=True)

fundamentus = tk.remover_seguradoras_e_rj(fundamentus)
