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

A Blitz Inteligente de Telemetria foi desenvolvido para automatizar esse processo e fornecer uma visão clara dos veículos que necessitam de atenção.

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

---

## 🤖 Evolução V2 — Arquitetura com Agentes de Auditoria

A versão 2 da Blitz Inteligente de Telemetria iniciou a evolução do projeto para uma arquitetura baseada em agentes especializados, inspirada em plataformas como **Pandada AI** e **V7 Go**.

A **Pandada AI** foi utilizada como referência para a experiência de análise conversacional de dados, em que o usuário pode carregar arquivos, consultar informações em linguagem natural e obter análises, gráficos e relatórios automatizados.

O **V7 Go** foi utilizado como referência para a estrutura de agentes aplicados a fluxos de auditoria, com foco na identificação de exceções, organização de evidências, geração de relatórios e apoio à tomada de decisão.

Nesta primeira etapa da V2, foi implementado o **Agente de Auditoria de Divergências**, responsável por consolidar os dados por veículo e gerar uma visão mais confiável da criticidade de cada placa.

### Responsabilidades do Agente de Auditoria

* Consolidar os registros por placa;
* Calcular a média oficial consolidada;
* Calcular a média alternativa consolidada;
* Calcular a divergência consolidada do período;
* Identificar a quantidade de dias críticos;
* Classificar o status consolidado do veículo;
* Definir uma prioridade operacional para análise;
* Apoiar a geração do ranking de veículos críticos.

Com essa mudança, a aplicação deixa de analisar apenas linhas isoladas da planilha e passa a considerar o comportamento consolidado do veículo no período analisado.

### Regras de classificação

A classificação dos veículos é realizada com base na divergência consolidada:

| Divergência consolidada | Status         |
| ----------------------: | -------------- |
|                  Até 5% | OK             |
|     Acima de 5% até 10% | Atenção        |
|            Acima de 10% | Crítico        |
|   Sem dados suficientes | Sem comparação |

Além do status consolidado, o agente também calcula a quantidade de **dias críticos**, considerando os dias em que a divergência diária ultrapassou 10%.

### Próximas evoluções previstas

* Criar um Agente de Diagnóstico para gerar explicações automáticas por veículo;
* Criar um Agente de Relatório para preparar o encaminhamento dos veículos críticos;
* Implementar histórico mensal por placa;
* Permitir análise dos últimos meses por veículo;
* Identificar reincidência de divergências;
* Gerar relatórios para os responsáveis pelas telemetrias;
* Registrar tratativas e retornos recebidos.

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