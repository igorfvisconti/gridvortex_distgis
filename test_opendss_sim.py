# -*- coding: utf-8 -*-
"""
Script de Teste Automatizado de Fluxo de Potencia OpenDSS
Validação de Casos Gerados e Auditoria de Conformidade PRODIST ANEEL
Metodologia DIST-GIS / Energisa GridVortex Challenge 2026
"""
import sys
import os

# Adiciona diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.simulators.opendss_builder import generate_opendss_script
from src.simulators.opendss_runner import OpenDSSRunner

def main():
    print("=" * 80)
    print("ENERGISA GRIDVORTEX - TESTE AUTOMATIZADO DE FLUXO DE POTENCIA OPENDSS")
    print("=" * 80)

    # 1. Gerar script DSS de teste
    substation_id = "SUB_MANE_GARRINCHA"
    feeder_id = "CTMT_01_BRASILIA"
    dist_id = 5160 # Energisa Paraíba / Grupo Energisa

    print(f"\n[1/3] Gerando script Master.dss e arquivos complementares...")
    master_dss_path = generate_opendss_script(
        feeder_id=feeder_id,
        substation_id=substation_id,
        dist_id=dist_id,
        kv_base=13.8,
        erve_kw=1500.0, # Estação de Recarga 1.5 MW
        output_dir="/workspace/scratch/test_opendss_cases"
    )
    print(f" -> Arquivo gerado em: {master_dss_path}")

    # 2. Executar simulação de fluxo de potência
    print(f"\n[2/3] Executando simulação de fluxo de potência em regime permanente...")
    runner = OpenDSSRunner(master_dss_path)
    results = runner.run_simulation()
    summary = results['summary']

    print(f" -> Motor de Execução: {summary['Execution_Engine']}")
    print(f" -> Total de Barras: {summary['Total_Buses']}")
    print(f" -> Total de Linhas: {summary['Total_Lines']}")
    print(f" -> Demanda Total: {summary['Total_Load_kW']:.1f} kW")
    print(f" -> Perdas Ativas: {summary['Active_Losses_kW']:.2f} kW ({summary['Loss_Percentage']:.2f}%)")
    print(f" -> Perdas Reativas: {summary['Reactive_Losses_kVar']:.2f} kVar")
    print(f" -> Tensão Mínima: {summary['Min_Voltage_pu']:.3f} p.u.")
    print(f" -> Tensão Máxima: {summary['Max_Voltage_pu']:.3f} p.u.")

    # 3. Auditoria de Níveis de Tensão (PRODIST Módulo 8)
    print(f"\n[3/3] Auditoria Regulatória PRODIST (Módulo 8 ANEEL):")
    print(f" -> Barras com Tensão Adequada (0.93 - 1.05 p.u.): {summary['PRODIST_Adequate_Buses']}")
    print(f" -> Barras com Tensão Precária (0.90 - 0.93 p.u.): {summary['PRODIST_Precarious_Buses']}")
    print(f" -> Barras com Tensão Crítica  (<0.90 / >1.05 p.u.): {summary['PRODIST_Critical_Buses']}")

    print("\n--- PERFIL DE TENSAO POR BARRA ---")
    df_buses = results['buses']
    print(df_buses[['Bus', 'kV_Base', 'V_pu', 'V_kV', 'Status_PRODIST']].to_string(index=False))

    if not results['lines'].empty:
        print("\n--- CARREGAMENTO DAS LINHAS MT ---")
        df_lines = results['lines']
        print(df_lines[['Line', 'From_Bus', 'To_Bus', 'Current_A', 'Loading_Pct', 'Status']].to_string(index=False))

    print("\n" + "=" * 80)
    print(f"RESULTADO FINAL DO TESTE DA REDE: {summary['Compliance_Status']}")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
