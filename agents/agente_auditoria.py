import pandas as pd


def classificar_status_por_divergencia(divergencia):
    """Classifica o veículo com base na divergência consolidada."""
    if pd.isna(divergencia):
        return "Sem comparação"
    elif divergencia > 10:
        return "Crítico"
    elif divergencia > 5:
        return "Atenção"
    else:
        return "OK"


def classificar_prioridade(status, dias_criticos):
    """Define a prioridade operacional com base no status e nos dias críticos."""
    if status == "Crítico" and dias_criticos >= 5:
        return "Alta"
    elif status == "Crítico":
        return "Média"
    elif status == "Atenção" and dias_criticos >= 3:
        return "Média"
    elif status == "Atenção":
        return "Baixa"
    else:
        return "Normal"


def executar_agente_auditoria(df):
    """
    Agente de Auditoria de Divergências.

    Recebe o DataFrame já processado pela Blitz e retorna uma análise
    consolidada por placa, considerando divergência consolidada,
    dias críticos, status e prioridade.
    """

    df_agente = df.copy()

    df_agente["%Média"] = pd.to_numeric(df_agente["%Média"], errors="coerce")
    df_agente["Media_Alternativa"] = pd.to_numeric(
        df_agente["Media_Alternativa"],
        errors="coerce"
    )
    df_agente["Divergencia"] = pd.to_numeric(
        df_agente["Divergencia"],
        errors="coerce"
    )

    analise_placas = (
        df_agente
        .groupby("Placa")
        .agg(
            telemetria_valida=("Telemetria Válida", "first"),
            dias_analisados=("Placa", "count"),
            dias_criticos=("Divergencia", lambda x: (x > 10).sum()),
            media_oficial_consolidada=("%Média", "mean"),
            media_alternativa_consolidada=("Media_Alternativa", "mean"),
        )
        .reset_index()
    )

    analise_placas["divergencia_consolidada"] = analise_placas.apply(
        lambda linha: abs(
            (
                linha["media_alternativa_consolidada"]
                - linha["media_oficial_consolidada"]
            )
            / linha["media_oficial_consolidada"]
        ) * 100
        if pd.notna(linha["media_oficial_consolidada"])
        and linha["media_oficial_consolidada"] != 0
        and pd.notna(linha["media_alternativa_consolidada"])
        else None,
        axis=1
    )

    analise_placas["status_consolidado"] = analise_placas[
        "divergencia_consolidada"
    ].apply(classificar_status_por_divergencia)

    analise_placas["prioridade"] = analise_placas.apply(
        lambda linha: classificar_prioridade(
            linha["status_consolidado"],
            linha["dias_criticos"]
        ),
        axis=1
    )

    return analise_placas