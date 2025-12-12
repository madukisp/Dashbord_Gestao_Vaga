
import json

def categorize_cargos(file_path):
    """
    Categoriza os cargos em um arquivo JSON com base em palavras-chave.

    Args:
        file_path (str): O caminho para o arquivo JSON.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        cargos_data = json.load(f)

    categorized_data = {}
    for cargo, old_category in cargos_data.items():
        cargo_upper = cargo.upper()
        new_category = "Não Classificado"

        # Hierarchical keywords
        if "DIRETOR" in cargo_upper:
            new_category = "DIRETOR"
        elif "GERENTE" in cargo_upper:
            new_category = "GERENTE"
        elif "SUPERVISOR" in cargo_upper or "SUPERINTENDENTE" in cargo_upper:
            new_category = "SUPERVISOR"
        elif "COORDENADOR" in cargo_upper or "COORD." in cargo_upper:
            new_category = "COORDENADOR"
        elif "LIDER" in cargo_upper:
            new_category = "SUPERVISOR" # As per previous logic
        elif "ASSESSOR" in cargo_upper:
            new_category = "ASSESSOR"
        
        # Role-based keywords
        elif "MEDICO" in cargo_upper or "MÉDICO" in cargo_upper or "CIRURGIAO" in cargo_upper or "PSIQUIATRA" in cargo_upper or "PEDIATRA" in cargo_upper or "GINECOLOGISTA" in cargo_upper or "DERMATOLOGISTA" in cargo_upper or "FISIATRA" in cargo_upper or "GERIATRA" in cargo_upper or "NEUROLOGISTA" in cargo_upper or "OFTALMOLOGISTA" in cargo_upper or "ORTOPEDISTA" in cargo_upper or "REUMATOLOGISTA" in cargo_upper or "DENTISTA" in cargo_upper or "ODONTO" in cargo_upper:
            new_category = "MEDICOS"
        elif "ENFERMAGEM" in cargo_upper or "ENFERMEIR" in cargo_upper:
            new_category = "ENFERMAGEM"
        elif "TECNICO" in cargo_upper or "TÉCNICO" in cargo_upper or "TEC." in cargo_upper or "TECNOLOGO" in cargo_upper:
            new_category = "TÉCNICO"
        elif "APRENDIZ" in cargo_upper:
            new_category = "APRENDIZ"

        # Multidisciplinary and Administrative
        elif "ANALISTA" in cargo_upper or "ASSISTENTE" in cargo_upper or "ADVOGADO" in cargo_upper or "COMPRADOR" in cargo_upper or "CONTROLLER" in cargo_upper or "ESCRITURARIO" in cargo_upper or "FATURISTA" in cargo_upper or "SECRETARIA" in cargo_upper or "FINANCEIRO" in cargo_upper or "PESSOAL" in cargo_upper or "RH" in cargo_upper or "DP" in cargo_upper or "OUVIDORIA" in cargo_upper or "ALMOXARIFE" in cargo_upper or "RECEPCIONISTA" in cargo_upper or "TESOUREIRO" in cargo_upper or "TELEFONISTA" in cargo_upper or "PATRIMONIO" in cargo_upper or "ADM" in cargo_upper or "ADMINISTRADOR" in cargo_upper:
            new_category = "ADMINISTRATIVO"
        
        elif "FISIOTERAPEUTA" in cargo_upper or "FONOAUDIOLOGO" in cargo_upper or "PSICOLOGO" in cargo_upper or "NUTRICIONISTA" in cargo_upper or "SOCIAL" in cargo_upper or "FARMACEUTICO" in cargo_upper or "BIOMEDICO" in cargo_upper or "BIOQUIMICO" in cargo_upper or "EDUCADOR FISICO" in cargo_upper or "TERAPEUTA OCUPACIONAL" in cargo_upper or "MUSICOTERAPEUTA" in cargo_upper or "PSICOPEDAGOGO" in cargo_upper:
            new_category = "MULTIDISCIPLINAR"

        # Operational
        elif "ACOMPANHANTE" in cargo_upper or "AGENTE" in cargo_upper or "AJUDANTE" in cargo_upper or "ARQUIVISTA" in cargo_upper or "ATENDENTE" in cargo_upper or "AUXILIAR" in cargo_upper or "COPEIR" in cargo_upper or "COSTUREIRA" in cargo_upper or "COZINHEIR" in cargo_upper or "CUIDADOR" in cargo_upper or "ENCARREGADO" in cargo_upper or "ESTAGIARIO" in cargo_upper or "FAXINEIR" in cargo_upper or "INSTRUMENTADOR" in cargo_upper or "JARDINEIRO" in cargo_upper or "LIMPADOR" in cargo_upper or "MAQUEIRO" in cargo_upper or "MENSAGEIRO" in cargo_upper or "MERENDEIRA" in cargo_upper or "MOTORISTA" in cargo_upper or "OFICIAL" in cargo_upper or "OPERADOR" in cargo_upper or "PORTEIRO" in cargo_upper or "RECREADOR" in cargo_upper or "ROUPEIRO" in cargo_upper or "SERVENTE" in cargo_upper or "VIGIA" in cargo_upper or "CONTROLADOR" in cargo_upper or "MANUTENCAO" in cargo_upper:
            new_category = "OPERACIONAL"

        # Ambiguous cases
        if "AUTONOMO" in cargo_upper or "Implantação" in cargo_upper:
            new_category = "Não Classificado"

        categorized_data[cargo] = new_category

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(categorized_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    categorize_cargos('cargos_niveis.json')
    print("Categorização concluída.")
