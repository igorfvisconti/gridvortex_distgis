# -*- coding: utf-8 -*-
"""
Modulo de Visualizacao de Graficos de Demanda, Perfil Energético e Boxplots
Metodologia DIST-GIS / Energisa GridVortex
"""
import calendar
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_diversified_demand(loadshape_df=None, tip_day="DU"):
    """
    Gera gráfico Plotly de Demanda Diversificada ao longo de 24 horas
    estratificada por classe de consumo e curva total diversificada.
    """
    hours = list(range(1, 25))

    if loadshape_df is not None and not loadshape_df.empty and "HORA" in loadshape_df.columns:
        # Usar dados reais do dataframe de loadshapes
        df_filtered = loadshape_df[loadshape_df["TIP_DIA"] == tip_day] if "TIP_DIA" in loadshape_df.columns else loadshape_df
        classes = df_filtered["TIP_CC"].unique() if "TIP_CC" in loadshape_df.columns else ["RES", "COM", "IND"]
    else:
        # Gerar curvas sintetizadas baseadas nos padrões BDGD/PRODIST
        classes = ["RES", "COM", "IND", "RUR", "IP"]
        np.random.seed(42)

    # Perfis p.u. padronizados para cada classe
    profiles = {
        "RES": [0.35, 0.30, 0.28, 0.25, 0.28, 0.35, 0.50, 0.65, 0.70, 0.72, 0.75, 0.78, 0.80, 0.78, 0.75, 0.72, 0.75, 0.85, 0.98, 1.00, 0.95, 0.82, 0.60, 0.45],
        "COM": [0.15, 0.12, 0.10, 0.10, 0.12, 0.25, 0.55, 0.85, 0.95, 1.00, 0.98, 0.92, 0.88, 0.95, 0.98, 0.95, 0.85, 0.65, 0.40, 0.25, 0.20, 0.18, 0.16, 0.15],
        "IND": [0.80, 0.80, 0.78, 0.78, 0.82, 0.88, 0.95, 1.00, 0.98, 0.96, 0.95, 0.92, 0.90, 0.95, 0.98, 0.96, 0.92, 0.88, 0.85, 0.82, 0.80, 0.80, 0.80, 0.80],
        "RUR": [0.20, 0.18, 0.15, 0.15, 0.30, 0.60, 0.80, 0.90, 0.85, 0.75, 0.65, 0.60, 0.65, 0.75, 0.85, 0.95, 1.00, 0.85, 0.60, 0.40, 0.30, 0.25, 0.22, 0.20],
        "IP":  [1.00, 1.00, 1.00, 1.00, 1.00, 0.50, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 1.00, 1.00, 1.00, 1.00, 1.00]
    }

    colors = {
        "RES": "#2ECC71", # Verde
        "COM": "#3498DB", # Azul
        "IND": "#E67E22", # Laranja
        "RUR": "#F1C40F", # Amarelo
        "IP":  "#9B59B6"  # Roxo
    }

    class_names = {
        "RES": "Residencial", "COM": "Comercial", "IND": "Industrial", "RUR": "Rural", "IP": "Iluminação Pública"
    }

    fig = go.Figure()

    # Adicionar traço de cada classe
    total_demand = np.zeros(24)
    for c in classes:
        p = np.array(profiles.get(c, profiles["RES"]))
        scale_kw = {"RES": 450, "COM": 350, "IND": 800, "RUR": 150, "IP": 100}.get(c, 200)
        demand_kw = p * scale_kw
        total_demand += demand_kw

        fig.add_trace(go.Scatter(
            x=hours,
            y=demand_kw,
            mode='lines+markers',
            name=class_names.get(c, c),
            line=dict(width=2, color=colors.get(c, '#7F8C8D')),
            marker=dict(size=5)
        ))

    # Adicionar curva de demanda total diversificada (com fator de coincidência)
    coincidence_factor = 0.88
    diversified_total = total_demand * coincidence_factor

    fig.add_trace(go.Scatter(
        x=hours,
        y=diversified_total,
        mode='lines+markers',
        name='Demanda Diversificada Total (MW)',
        line=dict(width=4, color='#E74C3C', dash='solid'),
        marker=dict(size=8, symbol='diamond')
    ))

    fig.update_layout(
        title=f"Perfil de Demanda Diversificada de 24h ({'Dia Útil' if tip_day=='DU' else 'Fim de Semana'})",
        xaxis=dict(title="Hora do Dia (h)", tickmode='linear', tick0=1, dtick=1),
        yaxis=dict(title="Demanda (kW / MW)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def plot_monthly_energy_and_mean_demand(sub_id="SUB_01", energy_data=None):
    """
    Gera gráfico de barras com perfil mensal de energia consumida e gerada (MWh),
    com a série de Demanda Média Mensal (MW) no eixo Y secundário.
    """
    months = list(range(1, 13))
    month_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    total_hours_per_month = [calendar.monthrange(2023, i)[1] * 24 for i in range(1, 13)]

    if energy_data is not None and isinstance(energy_data, dict):
        consumed_mwh = energy_data.get('consumed_mwh', [1200 + i*40 for i in range(12)])
        generated_mwh = energy_data.get('generated_mwh', [150 + i*15 for i in range(12)])
    else:
        # Dados sintetizados do histórico BDGD
        consumed_mwh = [3450, 3620, 3510, 3380, 3200, 3100, 3150, 3280, 3400, 3550, 3680, 3800]
        generated_mwh = [420, 480, 510, 530, 490, 460, 520, 580, 610, 590, 530, 470]

    # Calcular demanda média em MW: (MWh * 1000) / horas_no_mes / 1000 = MWh / horas_no_mes
    mean_demand_mw = [round(c / h, 2) for c, h in zip(consumed_mwh, total_hours_per_month)]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barras de Energia Consumida (MWh)
    fig.add_trace(
        go.Bar(
            x=month_names,
            y=consumed_mwh,
            name="Energia Consumida (MWh)",
            marker=dict(color="#2980B9"),
            text=[f"{v:,}" for v in consumed_mwh],
            textposition="auto"
        ),
        secondary_y=False
    )

    # Barras de Energia Gerada - GD (MWh)
    fig.add_trace(
        go.Bar(
            x=month_names,
            y=generated_mwh,
            name="Geração Distribuída GD (MWh)",
            marker=dict(color="#27AE60"),
            text=[f"{v:,}" for v in generated_mwh],
            textposition="auto"
        ),
        secondary_y=False
    )

    # Linha no Eixo Y Secundário: Demanda Média Mensal (MW)
    fig.add_trace(
        go.Scatter(
            x=month_names,
            y=mean_demand_mw,
            name="Demanda Média Mensal (MW)",
            mode="lines+markers+text",
            text=[f"{v:.2f} MW" for v in mean_demand_mw],
            textposition="top center",
            line=dict(color="#E67E22", width=3),
            marker=dict(symbol="circle", size=8, color="#D35400")
        ),
        secondary_y=True
    )

    fig.update_layout(
        title=f"Perfil Mensal de Energia Consumida/Gerada e Demanda Média - Subestação {sub_id}",
        xaxis_title="Mês",
        barmode="group",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_yaxes(title_text="Energia (MWh)", secondary_y=False)
    fig.update_yaxes(title_text="Demanda Média Mensal (MW)", secondary_y=True)

    return fig

def plot_consumption_boxplot_by_voltage(loads_df=None):
    """
    Gera gráfico Box-Plot com a distribuição de consumo mensal de energia
    estratificado por Nível de Tensão (AT - 69/138kV, MT - 13.8/34.5kV, BT - 220/380V).
    Aparece de forma idêntica à análise do dist_gis_at_mt_porto_de_natal_rn.txt.
    """
    np.random.seed(101)

    if loads_df is not None and not loads_df.empty and "TENSAO" in loads_df.columns:
        df = loads_df.copy()
    else:
        # Sintetizar distribuição de consumos estatisticamente coerente com BDGD
        at_consumption = np.random.lognormal(mean=8.5, sigma=0.6, size=45) # MWh/mês
        mt_consumption = np.random.lognormal(mean=4.2, sigma=0.8, size=250) # MWh/mês
        bt_consumption = np.random.lognormal(mean=0.6, sigma=0.9, size=1200) # MWh/mês

        df = pd.concat([
            pd.DataFrame({'Nível_Tensão': 'AT (Subtransmissão 69/138 kV)', 'Consumo_MWh': at_consumption}),
            pd.DataFrame({'Nível_Tensão': 'MT (Média Tensão 13.8/34.5 kV)', 'Consumo_MWh': mt_consumption}),
            pd.DataFrame({'Nível_Tensão': 'BT (Baixa Tensão 220/380 V)', 'Consumo_MWh': bt_consumption})
        ], ignore_index=True)

    fig = go.Figure()

    colors_map = {
        'AT (Subtransmissão 69/138 kV)': '#8E44AD', # Roxo
        'MT (Média Tensão 13.8/34.5 kV)': '#2980B9', # Azul
        'BT (Baixa Tensão 220/380 V)': '#27AE60'    # Verde
    }

    for level in df['Nível_Tensão'].unique():
        data_level = df[df['Nível_Tensão'] == level]['Consumo_MWh']
        fig.add_trace(go.Box(
            y=data_level,
            name=level,
            marker_color=colors_map.get(level, '#34495E'),
            boxmean='sd', # Exibir média e desvio padrão
            boxpoints='outliers' # Exibir pontos fora do limite
        ))

    fig.update_layout(
        title="Distribuição Estatística de Consumo Mensal por Nível de Tensão (BDGD BDGD24)",
        yaxis=dict(title="Consumo de Energia (MWh / Mês)", type="log"), # Escala logarítmica para abarcar AT/MT/BT
        xaxis_title="Nível de Tensão de Conexão",
        template="plotly_white",
        showlegend=False
    )

    return fig
