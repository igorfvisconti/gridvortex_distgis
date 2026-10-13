# -*- coding: utf-8 -*-
"""
Modulo de Mapeamento Georreferenciado e Visualizacao de Digrafos sobre Basemaps
Metodologia DIST-GIS / Energisa GridVortex
"""
import folium
from folium import plugins
import geopandas as gpd
import pandas as pd

def build_georeferenced_network_map(
    ungraphview_gdf=None,
    sim_results=None,
    dist_nome="Energisa Paraiba (EPB)",
    center_lat=-7.12,
    center_lon=-34.86,
    zoom_start=12
):
    """
    Cria mapa Folium interativo com a topologia da rede BDGD (digrafo georreferenciado)
    e a simbologia representativa das simulações do OpenDSS / ANAREDE sobre basemaps.
    """
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="CartoDB positron",
        control_scale=True
    )

    # Adicionar basemaps padrao
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)

    # Grupos de camadas
    fg_sub = folium.FeatureGroup(name="Subestacoes AT/MT", show=True)
    fg_lines = folium.FeatureGroup(name="Rede de Media Tensao (MT)", show=True)
    fg_trafos = folium.FeatureGroup(name="Transformadores MT/BT", show=True)
    fg_loads = folium.FeatureGroup(name="Cargas e Consumidores", show=True)
    fg_ders = folium.FeatureGroup(name="Recursos Energeticos (GD / EVCS / BESS)", show=True)
    fg_sim = folium.FeatureGroup(name="Resultados Simulacao (OpenDSS / ANAREDE)", show=True)

    # Coordenadas base para demonstracao interativa se GeoDataFrame for generico
    if ungraphview_gdf is None or ungraphview_gdf.empty:
        base_points = {
            'SUB_01': (-7.115, -34.862, "SE Moinho Central 69/13.8kV", 1.000, "Adequada"),
            'MID_01': (-7.120, -34.858, "Barramento Intermediario MT", 0.978, "Adequada"),
            'ERVE_01': (-7.128, -34.851, "Estacao Recarga VEs Porto 1.5MW", 0.942, "Adequada"),
            'SEC_01': (-7.132, -34.848, "Barramento Secundario BT", 0.938, "Adequada"),
            'CRIT_01': (-7.140, -34.840, "Barramento Ponta de Linha", 0.912, "Precaria")
        }

        # Subestacao
        folium.Marker(
            location=[-7.115, -34.862],
            popup="<b>Subestacao AT/MT:</b> SE Moinho Central<br><b>Tensao AT:</b> 69 kV<br><b>Tensao MT:</b> 13.8 kV<br><b>Capacidade:</b> 25 MVA",
            icon=folium.Icon(color="purple", icon="bolt", prefix="fa")
        ).add_to(fg_sub)

        # Linhas do Digrafo (Alimentador MT)
        line_coords = [
            [(-7.115, -34.862), (-7.120, -34.858)],
            [(-7.120, -34.858), (-7.128, -34.851)],
            [(-7.128, -34.851), (-7.132, -34.848)],
            [(-7.132, -34.848), (-7.140, -34.840)]
        ]

        for idx, coords in enumerate(line_coords):
            color = "#2ECC71" if idx < 3 else "#F39C12"
            folium.PolyLine(
                locations=coords,
                color=color,
                weight=5,
                opacity=0.85,
                popup=f"<b>Alimentador MT:</b> CTMT_01<br><b>Trecho:</b> L{idx+1}<br><b>Condutor:</b> AL 336 MCM<br><b>Carregamento:</b> {35 + idx*18}%"
            ).add_to(fg_lines)

        # Barras e Resultados de Simulacao
        if sim_results and 'buses' in sim_results and not sim_results['buses'].empty:
            df_b = sim_results['buses']
            for idx, row in df_b.iterrows():
                b_name = row['Bus']
                v_pu = row['V_pu']
                status = row['Status_PRODIST']
                color = row.get('Cor_PRODIST', '#2ECC71')
                
                lat = -7.115 - (idx * 0.006)
                lon = -34.862 + (idx * 0.005)

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=9,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.9,
                    popup=f"<b>Barra:</b> {b_name}<br><b>Tensao Calculada:</b> {v_pu:.3f} p.u. ({row['V_kV']} kV)<br><b>PRODIST:</b> <span style='color:{color}'><b>{status}</b></span>"
                ).add_to(fg_sim)
        else:
            for key, (lat, lon, name, v_pu, status) in base_points.items():
                color = "#2ECC71" if status == "Adequada" else "#F39C12"
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.9,
                    popup=f"<b>Barra:</b> {key}<br><b>Nome:</b> {name}<br><b>Tensao Calculada:</b> {v_pu:.3f} p.u.<br><b>Status PRODIST:</b> {status}"
                ).add_to(fg_sim)

        # Ponto de Recarga de VE (ERVE / EVCS)
        folium.Marker(
            location=[-7.128, -34.851],
            popup="<b>Recurso Energetico Distribuido:</b> Estacao de Recarga VEs (ERVE Porto)<br><b>Potencia Solicitada:</b> 1.5 MW<br><b>Tensao:</b> 13.8 kV",
            icon=folium.Icon(color="red", icon="car", prefix="fa")
        ).add_to(fg_ders)

    else:
        # Se GeoDataFrame BDGD real for fornecido
        for idx, row in ungraphview_gdf.iterrows():
            geom = row.geometry
            tab = row.get('TAB', 'SSDMT')

            if geom is not None and not geom.is_empty:
                if geom.geom_type == 'Point':
                    lat, lon = geom.y, geom.x
                    if tab == 'SUB':
                        folium.Marker(
                            location=[lat, lon],
                            popup=f"<b>Subestacao:</b> {row.get('NOME', 'SUB')}",
                            icon=folium.Icon(color="purple", icon="bolt", prefix="fa")
                        ).add_to(fg_sub)
                    elif tab in ['UGMT_tab', 'UGBT_tab']:
                        folium.Marker(
                            location=[lat, lon],
                            popup=f"<b>Geracao Distribuida:</b> {row.get('COD_ID', 'GD')}",
                            icon=folium.Icon(color="green", icon="sun-o", prefix="fa")
                        ).add_to(fg_ders)
                    else:
                        folium.CircleMarker(
                            location=[lat, lon],
                            radius=4,
                            color="#34495E",
                            fill=True
                        ).add_to(fg_loads)

                elif geom.geom_type in ['LineString', 'MultiLineString']:
                    coords = [[p[1], p[0]] for p in (geom.coords if geom.geom_type == 'LineString' else geom.geoms[0].coords)]
                    folium.PolyLine(
                        locations=coords,
                        color="#2980B9",
                        weight=3,
                        opacity=0.8
                    ).add_to(fg_lines)

    # Adicionar grupos ao mapa
    fg_sub.add_to(m)
    fg_lines.add_to(m)
    fg_trafos.add_to(m)
    fg_loads.add_to(m)
    fg_ders.add_to(m)
    fg_sim.add_to(m)

    # Adicionar controle de camadas e minimapa
    folium.LayerControl(collapsed=False).add_to(m)
    plugins.MiniMap(toggle_display=True).add_to(m)

    return m
