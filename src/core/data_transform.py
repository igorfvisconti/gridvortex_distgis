# -*- coding: utf-8 -*-
"""
Modulo de Transformacao e Limpeza de Dados BDGD / DIST-GIS
"""
import json
import pandas as pd
import geopandas as gpd

def unnest(gdf, nome_campo='atr3'):
    """Descompacta atributos JSON serializados (ex: informacoes de condutores/chaves)"""
    gdf = gdf.copy()
    if nome_campo not in gdf.columns:
        return gdf
    
    def parse_json(val):
        if isinstance(val, str):
            try:
                res = json.loads(val)
                return res[0] if isinstance(res, list) and len(res) > 0 else res
            except Exception:
                return {}
        return val if isinstance(val, dict) else {}

    gdf['atr_dict'] = gdf[nome_campo].apply(parse_json)
    norm_df = pd.json_normalize(gdf['atr_dict'])
    for col in norm_df.columns:
        if col not in gdf.columns:
            gdf[col] = norm_df[col].values
    return gdf.drop(columns=['atr_dict'])

def unnest2(gdf, nome_campo='atr3'):
    """Descompacta atributos de energia (ENE_01..12) e demanda (DEM_01..12)"""
    gdf = gdf.copy()
    if nome_campo not in gdf.columns:
        return gdf
        
    def parse_json(val):
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return {}
        return val if isinstance(val, dict) else {}

    gdf['atr_dict'] = gdf[nome_campo].apply(parse_json)
    norm_df = pd.json_normalize(gdf['atr_dict'])
    
    for k in norm_df.columns:
        if len(k) >= 5 and k[:3] in ('ENE', 'DEM', 'PNT'):
            gdf[k] = norm_df[k].apply(lambda s: float(s) if s is not None and str(s).replace('.','',1).isdigit() else 0.0).values
        else:
            gdf[k] = norm_df[k].values
            
    return gdf.drop(columns=['atr_dict'])

def dict_filt(dist=None, sub=None, untrat=None, ctmt=None, untrmt=None):
    """Cria dicionario de filtros SQL para BDGD"""
    filt = {}
    if dist: filt["DIST"] = dist
    if sub: filt["SUB"] = sub
    if untrat: filt["UNTRAT"] = untrat
    if ctmt: filt["CTXT"] = ctmt
    if untrmt: filt["UNTRMT"] = untrmt
    return filt

def where_opt(filtro_dict):
    """Gera lista de condicoes WHERE formatadas em SQL"""
    options = []
    for k, v in filtro_dict.items():
        if isinstance(v, list):
            options.append("(" + " OR ".join([f"{k}='{i_v}'" if isinstance(i_v, str) else f"{k}={i_v}" for i_v in v]) + ")")
        elif isinstance(v, str):
            options.append(f"{k}='{v}'")
        else:
            options.append(f"{k}={v}")
    return options
