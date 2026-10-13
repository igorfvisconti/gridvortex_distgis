import os

PROJECT_ID = os.environ.get('PROJECT_ID', 'poc-sagis')
DEFAULT_DATASET = os.environ.get('DATASET_ID', 'BDGD24')

ENERGISA_DISTRIBUTORS = {
    5160: {'nome': 'Energisa Paraíba (EPB)', 'uf': 'PB', 'dataset': 'BDGD24'},
    5161: {'nome': 'Energisa Borborema (EBO)', 'uf': 'PB', 'dataset': 'BDGD24'},
    390:  {'nome': 'Energisa Sergipe (ESE)', 'uf': 'SE', 'dataset': 'BDGD24'},
    389:  {'nome': 'Energisa Rondônia (ERO)', 'uf': 'RO', 'dataset': 'BDGD24'},
    391:  {'nome': 'Energisa Mato Grosso (EMT)', 'uf': 'MT', 'dataset': 'BDGD24'},
    392:  {'nome': 'Energisa Acre (EAC)', 'uf': 'AC', 'dataset': 'BDGD24'},
    393:  {'nome': 'Energisa Mato Grosso do Sul (EMS)', 'uf': 'MS', 'dataset': 'BDGD24'},
    394:  {'nome': 'Energisa Tocantins (ETO)', 'uf': 'TO', 'dataset': 'BDGD24'},
    395:  {'nome': 'Energisa Sul-Sudeste (ESS)', 'uf': 'SP/PR/MG', 'dataset': 'BDGD24'},
}

VOLTAGE_LEVELS = {
    'AT': 'Alta Tensão (Subtransmissão - 69 kV / 138 kV) -> Simulador ANAREDE (.pwf)',
    'MT': 'Média Tensão (Alimentadores - 13.8 kV / 34.5 kV) -> Simulador OpenDSS (.dss)',
    'BT': 'Baixa Tensão (Rede Secundária - 220V / 380V) -> Simulador OpenDSS (.dss)',
}
