# -*- coding: utf-8 -*-
"""
Gerador de Modelos e Scripts (.DSS) para o OpenDSS (Estudos de Media e Baixa Tensao - MT/BT)
"""
import os
import pandas as pd

def generate_opendss_script(
    feeder_id,
    substation_id,
    dist_id,
    kv_base=13.8,
    mva_sc3=150.0,
    mva_sc1=100.0,
    erve_kw=1500.0,
    output_dir="/workspace/scratch/opendss_cases"
):
    """
    Gera conjunto de scripts Master.dss e componentes para simulacao trifasica
    desequilibrada no OpenDSS para conexao de ERVE / BESS / GD.
    """
    feeder_dir = os.path.join(output_dir, str(dist_id), substation_id, feeder_id)
    os.makedirs(feeder_dir, exist_ok=True)

    master_dss_path = os.path.join(feeder_dir, "Master.dss")
    master_content = f"""!=============================================================================
! MODELO OPENDSS GERADO VIA DIST-GIS - ENERGISA GRIDVORTEX
! ALIMENTADOR MT: {feeder_id} | SUBESTACAO: {substation_id} | DIST: {dist_id}
!=============================================================================
Clear

New Circuit.SE_{substation_id}_{feeder_id} bus1=sub_bar basekv={kv_base} pu=1.00 MVAsc3={mva_sc3} MVAsc1={mva_sc1}

! Carregar Bibliotecas de Condutores e Curvas de Carga
Redirect LineCodes.dss
Redirect LoadShapes.dss

! Carregar Topologia da Rede MT
Redirect LinhasMT.dss
Redirect TrafosMTBT.dss
Redirect ChavesMT.dss

! Carregar Cargas e REDs
Redirect CargasMTBT.dss

! Insercao da Estacao de Recarga de Veiculo Eletrico (ERVE / EVCS)
New Load.ERVE_{feeder_id} Bus1=bar_erve kV={kv_base} kW={erve_kw} PF=0.95 Model=1 Class=1

Set voltagebases=[{kv_base}, 0.38, 0.22]
CalcVoltageBases

Set mode=daily stepsize=15m number=96
Solve

! Exportar Resultados de Tensao e Perdas
! Export Voltages
! Export Losses
"""
    with open(master_dss_path, "w", encoding="utf-8") as f:
        f.write(master_content)

    # LineCodes placeholder
    with open(os.path.join(feeder_dir, "LineCodes.dss"), "w", encoding="utf-8") as f:
        f.write("""New Linecode.AL_4AWG nphases=3 r1=0.5369 x1=0.5850 units=km
New Linecode.AL_336MCM nphases=3 r1=0.1685 x1=0.4430 units=km
""")

    # LoadShapes placeholder
    with open(os.path.join(feeder_dir, "LoadShapes.dss"), "w", encoding="utf-8") as f:
        f.write("""New Loadshape.RES_DU npts=96 minterval=15 Pmult=(0.3 0.3 0.25 0.25 0.3 0.4 0.5 0.6 0.7 0.8 0.85 0.9 0.95 1.0 0.9 0.85)
New Loadshape.COM_DU npts=96 minterval=15 Pmult=(0.1 0.1 0.1 0.1 0.2 0.5 0.8 0.9 1.0 1.0 0.95 0.9 0.85 0.8 0.7 0.5)
""")

    # LinhasMT placeholder
    with open(os.path.join(feeder_dir, "LinhasMT.dss"), "w", encoding="utf-8") as f:
        f.write(f"""New Line.L1 Bus1=sub_bar Bus2=bar_mid Linecode=AL_336MCM Length=2.5 Units=km
New Line.L2 Bus1=bar_mid Bus2=bar_erve Linecode=AL_4AWG Length=0.8 Units=km
""")

    # TrafosMTBT placeholder
    with open(os.path.join(feeder_dir, "TrafosMTBT.dss"), "w", encoding="utf-8") as f:
        f.write(f"""New Transformer.TR1 Buses=[sub_bar, bar_sec] kVs=[{kv_base}, 0.38] kVas=[112.5, 112.5] XHL=4.5
""")

    # ChavesMT placeholder
    with open(os.path.join(feeder_dir, "ChavesMT.dss"), "w", encoding="utf-8") as f:
        f.write("""New Line.SW1 Bus1=bar_mid Bus2=bar_sw Linecode=AL_4AWG Length=0.001 Units=km
New SwtControl.SW1_ctrl SwitchedObj=Line.SW1 Action=Close
""")

    # CargasMTBT placeholder
    with open(os.path.join(feeder_dir, "CargasMTBT.dss"), "w", encoding="utf-8") as f:
        f.write(f"""New Load.Carga_01 Bus1=bar_sec kV=0.22 kW=45 PF=0.92 Daily=RES_DU Model=1
""")

    return master_dss_path
