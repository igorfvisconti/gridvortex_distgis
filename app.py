# -*- coding: utf-8 -*-
"""
Dashboard Web Interativo (Streamlit MVP) - Energisa GridVortex Challenge 2026
Mapeamento BDGD, Visualização de Digrafos, Análise Energética e Simulação OpenDSS/ANAREDE
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Adicionar src ao PATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import ENERGISA_DISTRIBUTORS, VOLTAGE_LEVELS
from src.database.bigquery_client import get_bigquery_client, get_substations, geo2dist, query_ungraphview
from src.simulators.opendss_builder import generate_opendss_script
from src.simulators.opendss_runner import OpenDSSRunner
from src.simulators.anarede_builder import AnaredeBuilder
from src.visualization.charts import (
    plot_diversified_demand,
    plot_monthly_energy_and_mean_demand,
    plot_consumption_boxplot_by_voltage
)
from src.visualization.maps import build_georeferenced_network_map
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Energisa GridVortex - Plataforma DIST-GIS",
    page_icon="⚡",
    layout="wide"
)

# Header
st.title("⚡ Energisa GridVortex: Plataforma DIST-GIS & Diagnóstico de Redes")
st.caption("Solução Inteligente de Mapeamento BDGD (2016-2026), Simulação OpenDSS/ANAREDE e Análise Energética (Módulo 02)")

# Sidebar Configuration
st.sidebar.header("⚙️ Configurações da Concessionária & Estudo")

dist_id = st.sidebar.selectbox(
    "Distribuidora do Grupo Energisa:",
    options=list(ENERGISA_DISTRIBUTORS.keys()),
    format_func=lambda x: f"{ENERGISA_DISTRIBUTORS[x]['nome']} ({ENERGISA_DISTRIBUTORS[x]['uf']})"
)

voltage_level = st.sidebar.radio(
    "Nível de Tensão do Estudo:",
    options=["AT", "MT", "BT"],
    format_func=lambda x: f"{x} - {VOLTAGE_LEVELS[x].split('->')[0]}"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Parâmetros do Recurso Conectado (RED)")
red_type = st.sidebar.selectbox("Tipo de Recurso (RED):", ["Estação de Recarga VEs (ERVE)", "Geração Distribuída (GD)", "Sistema de Baterias (BESS)", "Carga Especial / Porto"])
red_power_kw = st.sidebar.number_input("Potência Solicitada (kW):", min_value=50.0, max_value=20000.0, value=1500.0 if voltage_level != "AT" else 16000.0, step=100.0)

# Abas Principais
tab_map, tab_charts, tab_sim, tab_export = st.tabs([
    "🗺️ Mapa Georreferenciado & Digrafo",
    "📊 Análise de Demanda & Consumo",
    "⚡ Simulador OpenDSS / ANAREDE",
    "📁 Projetos & Exportação"
])

# -----------------------------------------------------------------------------
# TAB 1: MAPA GEORREFERENCIADO E DIGRAFO TOPOLÓGICO
# -----------------------------------------------------------------------------
with tab_map:
    st.subheader(f"🗺️ Topologia Georreferenciada da Rede BDGD - {ENERGISA_DISTRIBUTORS[dist_id]['nome']}")

    col_m1, col_m2 = st.columns([3, 1])

    with col_m1:
        # Tenta recuperar resultados de simulação salvos na sessão
        sim_res = st.session_state.get('last_sim_results', None)

        # Gerar mapa interativo
        map_obj = build_georeferenced_network_map(
            dist_nome=ENERGISA_DISTRIBUTORS[dist_id]['nome'],
            sim_results=sim_res
        )
        st_folium(map_obj, width="100%", height=520)

    with col_m2:
        st.markdown("### 🔍 Legenda & Status PRODIST")
        st.markdown("""
        * 🟣 **Subestação AT/MT**: Ponto de suprimento principal
        * 🟢 **Tensão Adequada**: 0.93 - 1.05 p.u. (PRODIST)
        * 🟡 **Tensão Precária**: 0.90 - 0.93 p.u.
        * 🔴 **Tensão Crítica**: <0.90 p.u. ou >1.05 p.u.
        * 🚗 **RED Conectado**: Estação de Recarga / BESS / GD
        """)

        st.info("💡 Clique nos elementos do mapa para inspecionar os valores calculados de tensão (kV e p.u.) e carregamento.")

# -----------------------------------------------------------------------------
# TAB 2: ANÁLISE DE DEMANDA, PERFIL MENSAL E BOXPLOTS ESTATÍSTICOS
# -----------------------------------------------------------------------------
with tab_charts:
    st.subheader("📊 Indicadores Energéticos e Curvas de Cargas Estratificadas")

    tab_c1, tab_c2, tab_c3 = st.tabs([
        "📈 Demanda Diversificada (24h)",
        "📊 Perfil Mensal MWh + Demanda MW (Eixo Secundário)",
        "📦 Boxplots por Nível de Tensão (AT/MT/BT)"
    ])

    with tab_c1:
        st.markdown("#### Curvas de Demanda Diversificada de 24 Horas por Classe de Consumo")
        tip_dia = st.radio("Tipo de Dia:", ["DU (Dia Útil)", "SA (Sábado)", "DO (Domingo)"], horizontal=True)
        fig_dem = plot_diversified_demand(tip_day=tip_dia[:2])
        st.plotly_chart(fig_dem, use_container_width=True)

    with tab_c2:
        st.markdown("#### Perfil Mensal de Energia Consumida/Gerada (MWh) e Demanda Média Mensal (MW)")
        fig_monthly = plot_monthly_energy_and_mean_demand()
        st.plotly_chart(fig_monthly, use_container_width=True)
        st.caption("Nota: A demanda média mensal no eixo Y2 é calculada rigorosamente ponderando a energia acumulada pelas horas exatas de cada mês (24h x dias do mês).")

    with tab_c3:
        st.markdown("#### Distribuição Estatística de Consumos de Energia Estratificados por Nível de Tensão")
        fig_box = plot_consumption_boxplot_by_voltage()
        st.plotly_chart(fig_box, use_container_width=True)
        st.caption("Análise baseada no modelo estatístico do dist_gis_at_mt_porto_de_natal_rn.txt, exibindo quartis, mediana e outliers.")

# -----------------------------------------------------------------------------
# TAB 3: SIMULADOR DE FLUXO DE POTÊNCIA OPENDSS / ANAREDE
# -----------------------------------------------------------------------------
with tab_sim:
    st.subheader("⚡ Execução de Fluxo de Potência Trifásico Desequilibrado")

    col_s1, col_s2 = st.columns([1, 2])

    with col_s1:
        st.markdown("#### Configuração do Caso de Estudo")
        sub_id = st.text_input("Subestação Alvo:", value="SUB_MOINHO_CENTRAL")
        feeder_id = st.text_input("Alimentador / Circuito:", value="CTMT_01_PORTO")
        kv_base = st.number_input("Tensão Nominal (kV):", value=13.8 if voltage_level != "AT" else 69.0)

        run_btn = st.button("🚀 Executar Simulação de Fluxo de Potência", type="primary", use_container_width=True)

    with col_s2:
        if run_btn or 'last_sim_results' in st.session_state:
            if run_btn:
                with st.spinner("Compilando arquivo Master.dss e executando fluxo de potência..."):
                    # Gerar script e rodar
                    master_path = generate_opendss_script(
                        feeder_id=feeder_id,
                        substation_id=sub_id,
                        dist_id=dist_id,
                        kv_base=kv_base,
                        erve_kw=red_power_kw
                    )
                    runner = OpenDSSRunner(master_path)
                    res = runner.run_simulation()
                    st.session_state['last_sim_results'] = res

            res = st.session_state['last_sim_results']
            summary = res['summary']

            st.success(f"Simulação Concluída com Sucesso! Status: **{summary['Compliance_Status']}**")

            # Métricas
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tensão Mínima", f"{summary['Min_Voltage_pu']:.3f} p.u.")
            m2.metric("Tensão Máxima", f"{summary['Max_Voltage_pu']:.3f} p.u.")
            m3.metric("Perdas Ativas", f"{summary['Active_Losses_kW']:.1f} kW ({summary['Loss_Percentage']:.2f}%)")
            m4.metric("Auditoria PRODIST", f"{summary['PRODIST_Adequate_Buses']} / {summary['Total_Buses']} Aprovadas")

            st.markdown("##### Perfil de Tensão por Barra Auditado")
            st.dataframe(res['buses'], use_container_width=True)

            if not res['lines'].empty:
                st.markdown("##### Carregamento e Capacidade dos Condutores")
                st.dataframe(res['lines'], use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: PROJETOS & EXPORTAÇÃO
# -----------------------------------------------------------------------------
with tab_export:
    st.subheader("📁 Arquivos Gerados e Exportação de Pacotes")

    st.markdown("""
    Você pode fazer o download do código fonte do projeto modularizado, scripts do OpenDSS (`.dss`),
    cartões do ANAREDE (`.pwf`) e planilhas de cronograma/orçamento:
    """)

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.info("📦 **Projeto Python Modular Completo (ZIP)**")
        st.markdown("Arquivo `gridvortex_distgis-v2.zip` pronto para implantação em produção ou no ambiente de nuvem da Energisa.")

    with col_e2:
        st.info("📊 **Planilha Financeira & Cronograma (XLSX)**")
        st.markdown("Arquivo `cronograma_orcamento_gridvortex_cepel.xlsx` com o planejamento de 10 semanas para a Fase Demo.")

# Footer
st.markdown("---")
st.caption("Energisa GridVortex Challenge 2026 | Desenvolvido por Pesquisadores do CEPEL | Módulo 02 - Diagnóstico Integrado")
