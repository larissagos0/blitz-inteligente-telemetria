import pandas as pd


def gerar_diagnostico_veiculo(dados_veiculo):
    """Gera um diagnótisco textual com base nos dados consolidados do veículo.

     Espera receber uma linha da análise consolidada gerada pelo Agente de Auditoria.    
    """

    placa = dados_veiculo.get("Placa", "Não informada")
    status = dados_veiculo.get("status_consolidado", "Sem status")
    prioridade = dados_veiculo.get("prioridade", "Não definida")
    dias_validos = dados_veiculo.get("dias_analisados", 0)
    dias_criticos = dados_veiculo.get("dias_criticos", 0)
    divergencia = dados_veiculo.get("divergencia_consolidada", None)
    telemetria = dados_veiculo.get("telemetria_valida", "Não informada")

    if pd.isna(divergencia):
      divergencia_texto = "não disponível"
    else:
      divergencia_texto = f"{divergencia:.2f}%"

    if prioridade == "Validar amostra":
       return (
          f"A placa {placa} possui apenas {dias_validos} dia(s) válido(s) para comparação. "
          f"Apesar do status consolidado estar como {status}, a amostra é pequena. "
          f"Recomenda-se validar se há dados suficientes antes de encaminhar uma tratativa formal."
       )
    
    if status == "Crítico":
       return (
          f"A placa {placa} foi classificada como crítica no consolidado do período. "
          f"A divergência consolidada foi de {divergencia_texto}, com {dias_criticos} dia(s) crítico(s) "
          f"em {dias_validos} dia(s) válido(s). A telemetria válida considerada foi {telemetria}. "
          f"Prioridade operacional: {prioridade}. Recomenda-se priorizar a validação da telemetria, "
          f"verificando possíveis inconsistências de leitura."
       )
    
    if status == "Atenção": 
       return (
          f"A placa {placa} apresentou divergência moderada no consolidado do período. "
          f"A divergência consolidada foi de {divergencia_texto}, com {dias_criticos} dia(s) crítico(s) "
          f"em {dias_validos} dia(s) válido(s). Recomenda-se acompanhar o comportamento do veículo "
          f"nas próximas análises antes de abrir uma tratativa prioritária."
       )
    
    if status == "OK":
       if dias_criticos >0:
          
          return (
            f"A placa {placa} está dentro do padrão esperado no consolidado do período, "
            f"com divergência consolidada de {divergencia_texto}. Apesar disso, houve {dias_criticos} "
            f"dia(s) crítico(s), indicando oscilações pontuais que podem ser acompanhadas."
          )
       
       return (
          f"A placa {placa} está dentro do padrão esperado no consolidado do período. "
          f"A divergência consolidada foi de {divergencia_texto}, sem dias críticos registrados."
        )
    
    return (
       f"Não foi possível gerar um diagnóstico conclusivo para a placa {placa}, "
       f"pois os dados disponíveis não permitem uma comparação confiável entre as telemetrias."
    )
    
       