import pandas as pd

def gerar_relatorio_criticos(analise_agente):
    """
    Gera um relatório textual dos veículos críticos consolidados.

    Recebe o DataFrame consolidado pelo Agende de Auditoria.
    """

    veiculos_criticos = (
        analise_agente[analise_agente["status_consolidado"] == "Crítico"]
        .sort_values(by="divergencia_consolidada", ascending=False)
        .copy()
    )

    if veiculos_criticos.empty:
        return "Nenhum veículo crítico identificado no consolidado do período."
    
    total_criticos = len(veiculos_criticos)
    prioridade_alta = len(veiculos_criticos[veiculos_criticos["prioridade"] == "Alta"])
    prioridade_media = len(veiculos_criticos[veiculos_criticos["prioridade"] == "Média"])
    prioridade_baixa = len(veiculos_criticos[veiculos_criticos["prioridade"] == "Baixa"])
    validar_amostra = len(veiculos_criticos[veiculos_criticos["prioridade"] == "Validar amostra"])

    maior_divergencia = veiculos_criticos["divergencia_consolidada"].max()
    media_divergencia = veiculos_criticos["divergencia_consolidada"].mean()

    relatorio = f"""
 
 ## 📄 Relatório de Veículos Críticos

 ### Resumo executivo

 Foram identificados **{total_criticos} veículo(s) crítico(s)** no consolidado do período.

  - Prioridade Alta: {prioridade_alta}
  - Prioridade Média: {prioridade_media}
  - Prioridade Baixa: {prioridade_baixa}
  - Validar amostra: {validar_amostra}
  - Maior divergência consolidada: {maior_divergencia:.2f}%
  - Média de divergência dos críticos: {media_divergencia:.2f}%

 ### Veículos críticos identificados
 """
    
    for _, linha in veiculos_criticos.iterrows():
        placa = linha["Placa"]
        telemetria = linha["telemetria_valida"]
        dias_validos = linha["dias_analisados"]
        dias_criticos = linha["dias_criticos"]
        divergencia = linha["divergencia_consolidada"]
        prioridade = linha["prioridade"]

        relatorio += f"""
  ### {placa}
  - Telemetria Válida: {telemetria}
  - Dias válidos: {dias_validos}
  - Dias críticos: {dias_criticos}
  - Divergência consolidada: {divergencia:.2f}%
  - Prioridade operacional: {prioridade}
  """
        if prioridade == "Validar amostra":
            relatorio += (
                "- Observação: a amostra possui poucos dias válidos. "
                "Recomenda-se validar a representatividade dos dados antes de abrir uma tratativa formal.\n "

            )

        elif prioridade == "Alta":
            relatorio += (
                "- Recomendação: priorizar análise da telemetria, pois há recorrência relevante de dias críticos.\n"

            )

        elif prioridade == "Média":
            relatorio += (
                "- Recomendação: avaliar os registros críticos e verificar possível inconsistência recorrente.\n"

            )

        elif prioridade == "Baixa":
            relatorio += (
                "- Recomendação: acompanhar veículo e validar se divergência foi pontual.\n"
            )

    relatorio += """
### Recomendações gerais

- Validar os veículos com maior divergência consolidada;
- Verificar casos com média alternativa ou oficial zerada;
- Priorizar veículos com maior quantidade de dias críticos;
- Separar os casos por telemetria responsável;
- Registrar o retorno da análise para acompanhamento futuro.
"""

    return relatorio  