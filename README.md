# ⚡ Energisa GridVortex - Plataforma DIST-GIS & Diagnóstico Integrado de Redes (Módulo 02)

## 📋 Sobre o Projeto
Esta aplicação foi desenvolvida por pesquisadores do **CEPEL** para o **GridVortex Challenge 2026 (Grupo Energisa)**. Ela implementa a metodologia **DIST-GIS** para automação de estudos de fluxo de potência em Média/Baixa Tensão (OpenDSS) e Alta Tensão (ANAREDE), integrando a Base de Dados Geográficos da Distribuição (**BDGD BDGD24**) de todas as 9 concessionárias do Grupo Energisa (EPB, ESE, ERO, EMT, EAC, EMS, ETO, ESS, EBO).

## 🚀 Estrutura do Projeto
```text
gridvortex_distgis/
├── app.py                      # Dashboard Web Interativo (Streamlit MVP)
├── test_opendss_sim.py         # Script de Teste Automático de Fluxo de Potência
├── config.py                  # Mapeamento das 9 distribuidoras Energisa e constantes
├── requirements.txt            # Dependências da aplicação
├── README.md                   # Documentação do projeto
└── src/
    ├── database/
    │   └── bigquery_client.py  # Autenticação (credenciais_bq) e consultas BDGD/ARAT
    ├── core/
    │   ├── data_transform.py  # Ingestão e unnesting de atributos JSON (atr2/atr3)
    │   └── graph_topology.py  # Algoritmos de grafos (NetworkX) e limpeza de folhas mortas
    ├── simulators/
    │   ├── anarede_builder.py # Motor de geração de casos PWF/SAV para Alta Tensão (ANAREDE)
    │   ├── opendss_builder.py # Motor de geração de scripts DSS para MT/BT (OpenDSS)
    │   └── opendss_runner.py  # Executor e Validador de Fluxo de Potência (PRODIST ANEEL)
    └── visualization/
        ├── charts.py          # Gráficos de Demanda Diversificada, Perfil Mensal MWh+MW e Boxplots
        └── maps.py            # Mapa Interativo Folium com Digrafo Topológico e Resultados sobre Basemaps
```

## 🛠️ Como Executar

### 1. Teste Automatizado via Terminal (CLI):
```bash
python test_opendss_sim.py
```

### 2. Dashboard Web Interativo no Streamlit:
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📊 Funcionalidades
1. **Mapa Georreferenciado e Digrafo Topológico sobre Basemaps**: Exibição da infraestrutura BDGD e overlay de tensões p.u. e carregamento de condutores com código de cores PRODIST.
2. **Gráficos de Demanda Diversificada (24h)**: Curvas de consumo por classe (Residencial, Comercial, Industrial, Rural, IP) e pico diversificado total.
3. **Perfil Mensal MWh e Demanda Média MW (Eixo Secundário)**: Histórico mensal de consumo e geração com cálculo no eixo Y2.
4. **Box-Plots Estatísticos por Nível de Tensão**: Distribuição de consumos mensal estratificada em AT, MT e BT.
5. **Auditoria Regulatória PRODIST (Módulo 8 ANEEL)**: Classificação automática das barras em Tensão Adequada (0.93 - 1.05 p.u.), Precária (0.90 - 0.93 p.u.) e Crítica (<0.90 p.u. ou >1.05 p.u.).
