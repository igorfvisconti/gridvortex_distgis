# -*- coding: utf-8 -*-
"""
Gerador de Casos e Cartoes (.PWF / .SAV) para o ANAREDE (Estudos de Alta Tensao - AT)
Metodologia DIST-GIS / Energisa GridVortex
"""
import os
import pandas as pd

def write_pwf_card(title, data_df, format_specs=None):
    """Gera bloco do arquivo PWF formatado com delimitadores 99999"""
    lines = [f"({title}", f"{title}"]
    for _, row in data_df.iterrows():
        line_str = ""
        for col in data_df.columns:
            val = str(row[col]) if pd.notna(row[col]) else ""
            line_str += f"{val:>10}"
        lines.append(line_str)
    lines.append("99999")
    return "\n".join(lines) + "\n"

def build_anarede_pwf_case(
    dist_nome="Energisa Paraíba (EPB)",
    uf="PB",
    mes=12,
    substation_name="SE_MOINHO",
    base_kv=69.0,
    added_load_mw=16.0,
    output_dir="/workspace/scratch/anarede_cases"
):
    """
    Gera o arquivo principal .PWF do ANAREDE para avaliacao de impacto de conexao
    de grande carga/RED na rede de Subtransmissao (AT)
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"principal_{uf}_mes{mes:02d}.pwf")

    pwf_content = f"""(=============================================================================
( PROJETO GRIDVORTEX ENERGISA - ESTUDO DE CONEXAO DE CARGA AT ({base_kv} kV)
( DISTRIBUIDORA: {dist_nome} ({uf}) - SUBESTACAO: {substation_name}
( CARGA ADICIONADA: {added_load_mw} MW - MES DE REFERENCIA: {mes:02d}
(=============================================================================
REST
2
rede_basica_2025.sav
ARQV INIC
SIM

DMTE
AREA 743                S TENS I
99999

DMFL
AREA 743                S TENS I
99999

DBAR
(NUM) O G NOME      GL V   A  PG    QG    PL    QL    ARE VF
9001  P  1 {substation_name[:6]:6s} {base_kv:4.1f} 743 1 1.0 0.0 {added_load_mw:6.1f} {added_load_mw*0.39:6.1f}
99999

EXLF IANG

TITU
CASO BASE COM ADICAO DE CARGA DE {added_load_mw} MW NO PORTO / SUBESTACAO {substation_name}

RELA RLIN AREA
743

FIM
"""
    with open(filename, "w", encoding="latin-1") as f:
        f.write(pwf_content)

    return filename

class AnaredeBuilder:
    """Interface Orientada a Objetos para o ANAREDE"""
    def __init__(self, dist_nome, uf):
        self.dist_nome = dist_nome
        self.uf = uf

    def build_case(self, substation_name, added_load_mw=16.0, base_kv=69.0, mes=12):
        return build_anarede_pwf_case(
            dist_nome=self.dist_nome,
            uf=self.uf,
            mes=mes,
            substation_name=substation_name,
            base_kv=base_kv,
            added_load_mw=added_load_mw
        )
