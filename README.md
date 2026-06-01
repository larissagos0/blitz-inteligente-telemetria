# 🚚 Blitz Inteligente de Telemetria

Sistema desenvolvido para auditoria inteligente de consumo de combustível e validação de telemetria de veículos pesados.

O objetivo é identificar divergências entre diferentes fontes de telemetria, destacando veículos com possíveis inconsistências de dados e apoiando a tomada de decisão operacional.

---

## 📋 Problema

Em operações logísticas, diferentes sistemas de telemetria podem apresentar resultados divergentes para um mesmo veículo.

A análise manual desses dados exige tempo e dificulta a identificação rápida de possíveis falhas de sensores, inconsistências de abastecimento ou problemas de integração.

O Blitz Inteligente automatiza essa análise e fornece uma visão executiva dos resultados.

---

## 🚀 Funcionalidades

### 📊 Dashboard Executivo

- KPIs de auditoria
- Distribuição dos status de validação
- Insights automáticos
- Ranking dos veículos mais críticos

### 🤖 Diagnóstico Inteligente

- Seleção individual de veículos
- Análise automática das divergências
- Score de confiabilidade
- Recomendações baseadas no status encontrado

### 📋 Auditoria Completa

- Visualização de todos os registros
- Busca por placa
- Filtro por status
- Paginação dos resultados

### 📥 Relatórios

- Exportação para Excel
- Relatório consolidado da auditoria
- Possibilidade de exportação filtrada por status

---

## 🧠 Regras de Negócio

### Classificação das Divergências

| Divergência | Status |
|------------|---------|
| Até 5% | ✅ OK |
| Entre 5% e 15% | ⚠️ Atenção |
| Acima de 15% | ❌ Crítico |

### Baixa Rodagem

Veículos com menos de 30 km válidos são classificados como:

```
Baixa Rodagem
```

para evitar análises distorcidas por amostras insuficientes.

---

## 🛠️ Tecnologias Utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- OpenPyXL

---

## 📈 Fluxo de Processamento

1. Importação da planilha Excel
2. Extração dos dados das telemetrias
3. Cálculo das médias alternativas
4. Comparação entre telemetrias
5. Cálculo das divergências
6. Classificação dos veículos
7. Geração dos insights
8. Exportação dos relatórios

---

## 💡 Diferenciais

- Interface intuitiva
- Diagnóstico inteligente por veículo
- Auditoria automatizada
- Identificação rápida de inconsistências
- Apoio à tomada de decisão operacional

---

## ▶️ Como Executar

Clone o projeto:

```bash
git clone URL_DO_REPOSITORIO
```

Acesse a pasta:

```bash
cd hackathon_telemetria
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute a aplicação:

```bash
streamlit run app.py
```



LinkedIn:
https://www.linkedin.com/in/larissagos/
