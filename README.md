# 🚚 Blitz Inteligente de Telemetria

Sistema desenvolvido para auditoria inteligente de consumo de combustível e validação de telemetria de veículos pesados.

A solução combina análise de dados, dashboards executivos e Inteligência Artificial Generativa para identificar inconsistências, priorizar tratativas e apoiar a tomada de decisão operacional.

---

## 📋 Problema

Em operações logísticas, diferentes sistemas de telemetria podem apresentar resultados divergentes para um mesmo veículo.

Essas inconsistências dificultam:

- A validação dos dados operacionais
- A identificação de falhas de telemetria
- A análise de consumo de combustível
- A priorização de tratativas
- A tomada de decisão gerencial

O Blitz Inteligente de Telemetria foi desenvolvido para automatizar esse processo e fornecer uma visão clara dos veículos que necessitam de atenção.

---

## 🎯 Objetivo

Automatizar a auditoria de dados de telemetria, identificando divergências entre diferentes fontes de informação e fornecendo insights para a operação.

---

## 🚀 Funcionalidades

- Upload de planilhas Excel
- Tratamento automático dos dados
- Comparação entre telemetrias
- Cálculo automático de divergências
- Classificação de criticidade dos veículos
- Dashboard executivo com indicadores
- Auditoria completa com filtros
- Relatórios dos veículos mais críticos
- Diagnóstico automático baseado em regras de negócio
- Agente de Auditoria com IA Generativa
- Consultas em linguagem natural

---

## 📊 Módulos do Sistema

### 📈 Dashboard

Visão executiva da operação contendo:

- Indicadores principais
- Veículos mais críticos
- Ranking de divergências
- Resumo da auditoria

### 🧠 Análise IA

Realiza diagnóstico individual dos veículos utilizando regras de negócio e Inteligência Artificial.

Permite identificar:

- Possíveis causas da divergência
- Impactos operacionais
- Recomendações de ação

### 📋 Auditoria Completa

Exibe toda a base processada com filtros e recursos para investigação dos dados.

### 📁 Relatórios

Disponibiliza relatórios e análises dos veículos auditados.

---

## 🤖 Inteligência Artificial

O sistema utiliza a API Google Gemini para atuar como um Agente de Auditoria Inteligente.

O agente interpreta os resultados da auditoria e responde perguntas em linguagem natural, transformando dados técnicos em recomendações operacionais.

### Exemplos de perguntas

- Qual veículo devo priorizar?
- Faça um resumo dos veículos críticos.
- Quais são os maiores riscos encontrados?
- Quais ações a operação deve executar primeiro?
- Explique as principais divergências encontradas.

---

## 🏗️ Fluxo da Solução

```text
Planilha Excel
        ↓
Tratamento dos Dados
        ↓
Validação das Telemetrias
        ↓
Cálculo das Divergências
        ↓
Classificação dos Veículos
        ↓
Dashboard e Auditoria
        ↓
Agente de IA Generativa
        ↓
Recomendações Operacionais
```

---

## 🛠️ Tecnologias Utilizadas

- Python
- Streamlit
- Pandas
- Plotly
- OpenPyXL
- Google Gemini API
- Git
- GitHub

---

## ✨ Diferenciais

- Interface intuitiva
- Auditoria automatizada
- Diagnóstico inteligente por veículo
- Identificação rápida de inconsistências
- Dashboard executivo
- Integração com IA Generativa
- Agente conversacional especializado em telemetria
- Consultas em linguagem natural

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

Configure sua chave da API Gemini em:

```toml
.streamlit/secrets.toml
```

Exemplo:

```toml
GEMINI_API_KEY = "SUA_CHAVE_AQUI"
```

Execute a aplicação:

```bash
streamlit run app.py
```

---

## 📌 Caso de Uso

O sistema foi desenvolvido como solução para um Hackathon de Inteligência Artificial voltado à otimização da auditoria de telemetria e apoio à tomada de decisão em operações logísticas.

---

## 👩‍💻 Autora

Larissa Garcia

LinkedIn:
https://www.linkedin.com/in/larissagos/

GitHub:
https://github.com/larissagos0