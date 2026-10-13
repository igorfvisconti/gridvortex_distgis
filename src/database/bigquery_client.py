# -*- coding: utf-8 -*-
"""
Modulo de Conexao e Consultas ao BigQuery
Metodologia DIST-GIS / Energisa GridVortex
"""
import os
from json import loads
from requests import get
import pandas as pd
import geopandas as gpd

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    HAS_BIGQUERY = True
except ImportError:
    HAS_BIGQUERY = False

def credenciais_bq(
    dropbox_url="https://www.dropbox.com/scl/fi/e1mc73r2r1jbhokenxiw2/poc-sagis-62a99e1335e9.json?rlkey=xrfi7t8h9i2m1vnp900ziow77&dl=1"
):
    """Cached credential loading from remote Dropbox JSON or local fallback"""
    if not HAS_BIGQUERY:
        print("Module google-cloud-bigquery not installed. Running in offline/simulation mode.")
        return None
        
    try:
        response = get(dropbox_url, timeout=30)
        response.raise_for_status()

        if not response.text.strip():
            raise ValueError("Empty response from Dropbox")

        credentials_info = loads(response.text)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        print("Remote credential query successful")
        return credentials

    except Exception as e:
        print(f"Error loading remote credentials: {str(e)}")
        cred_path = os.path.join(os.environ.get('WORKING_DIR', ''), 'poc-sagis-62a99e1335e9.json')
        if os.path.exists(cred_path):
            print("Local credential query successful")
            return service_account.Credentials.from_service_account_file(cred_path)
        raise e

def get_bigquery_client(project_id="poc-sagis", credentials=None):
    """Retorna cliente BigQuery autenticado ou Mock Client se offline"""
    if not HAS_BIGQUERY:
        return MockBigQueryClient(project_id)
        
    if credentials is None:
        try:
            credentials = credenciais_bq()
        except Exception:
            credentials = None
    if credentials:
        return bigquery.Client(project=project_id, credentials=credentials)
    return bigquery.Client(project=project_id)

class MockBigQueryClient:
    def __init__(self, project="poc-sagis"):
        self.project = project
        
    def query(self, query_str, job_config=None):
        return MockQueryJob()

class MockQueryJob:
    def to_geodataframe(self, geography_column='Shape'):
        return gpd.GeoDataFrame({
            'COD_ID': ['SUB_01', 'SUB_02'],
            'NOME': ['SE Moinho Potiguar', 'SE Natal Centro'],
            'Shape': gpd.GeoSeries.from_wkt(['POINT(-35.2  -5.78)', 'POINT(-35.21 -5.79)'])
        }, geometry='Shape', crs="EPSG:4326")
        
    def to_dataframe(self):
        return pd.DataFrame({
            'COD_ID': ['CTMT_01'],
            'NOME': ['Alimentador Centro'],
            'PAC_INI': ['PAC_001']
        })

def get_substations(client, dist_id, dataset_id="BDGD24"):
    """Consulta todas as subestacoes de uma distribuidora"""
    query = f"""
        SELECT COD_ID, NOME, ST_CENTROID(Shape) AS Shape 
        FROM `{getattr(client, 'project', 'poc-sagis')}.{dataset_id}.SUB` 
        WHERE DIST={dist_id}
    """
    return client.query(query).to_geodataframe(geography_column='Shape')

def geo2dist(client, lat, lon, dataset_id="BDGD24", table_id="UNGRAPHVIEW", tab_id="SSDMT", top_x=5):
    """Busca espacial dos circuitos/alimentadores MT mais proximos de um ponto (Lat/Lon)"""
    sql = f"""
        SELECT DIST_NOME, DIST, CONJ, SUB_NOME, SUB, UNTRAT, CTXT, 
               ROUND(ST_DISTANCE(ST_GEOGPOINT({lon}, {lat}), Shape)) AS distance, Shape 
        FROM `{getattr(client, 'project', 'poc-sagis')}.{dataset_id}.{table_id}` 
        WHERE TAB='{tab_id}' 
        ORDER BY distance LIMIT {top_x}
    """
    return client.query(sql).to_geodataframe(geography_column='Shape')

def query_ungraphview(client, dist_id, sub_id=None, ctxt_id=None, dataset_id="BDGD24", levels=["MT", "BT"]):
    """Consulta os elementos topologicos da rede UNGRAPHVIEW"""
    where_clauses = [f"DIST={dist_id}"]
    if sub_id:
        where_clauses.append(f"SUB='{sub_id}'")
    if ctxt_id:
        where_clauses.append(f"CTXT='{ctxt_id}'")

    tables = []
    if "MT" in levels:
        tables.extend(['SSDMT', 'UNCRMT', 'UNSEMT', 'UNREMT', 'UNTRMT', 'UCMT_tab', 'UGMT_tab'])
    if "BT" in levels:
        tables.extend(['SSDBT', 'UCBT_tab', 'UGBT_tab', 'PIP', 'RAMLIG', 'UNSEBT'])
    if "AT" in levels:
        tables.extend(['SSDAT', 'CTAT', 'UCAT_tab', 'UGAT_tab', 'UNTRAT', 'UNSEAT'])

    tabs_str = ", ".join([f"'{t}'" for t in set(tables)])
    w_opt = " AND ".join(where_clauses)

    query = f"""
        SELECT * FROM `{getattr(client, 'project', 'poc-sagis')}.{dataset_id}.UNGRAPHVIEW`
        WHERE TAB IN ({tabs_str}) AND {w_opt}
    """
    return client.query(query).to_geodataframe(geography_column='Shape')

def query_loadshape_pu(client, dist_id, tip_ccs, dataset_id="BDGD24"):
    """Consulta curvas de carga normalizadas (P.U.) por classe de consumo"""
    if len(tip_ccs) == 1:
        tip_str = f"('{list(tip_ccs)[0]}')"
    else:
        tip_str = str(tuple(tip_ccs))
    query = f"""
        SELECT * FROM `{getattr(client, 'project', 'poc-sagis')}.{dataset_id}.LOADSHAPE_PU`
        WHERE DIST={dist_id} AND TIP_CC IN {tip_str}
        ORDER BY DIST, TIP_CC, TIP_DIA, HORA
    """
    return client.query(query).to_dataframe()
