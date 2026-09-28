
# Projeto Prático: Plataforma de Inteligência Territorial e Risco Socioeconômico

## 1. Visão Geral do Projeto

O objetivo deste projeto é construir um **Data Lakehouse Analítico** moderno e automatizado para ingerir, transformar, cruzar e disponibilizar indicadores demográficos e socioeconômicos do **IBGE** combinados com dados abertos de alta complexidade (**INMET** ou **CAGED/MTE**).

Este projeto é destinado ao trabalho em **dupla**. A organização interna, distribuição de responsabilidades, arquitetura de pipeline e definição de padrões de engenharia de dados devem ser decididas e gerenciadas de forma **autônoma** pela equipe.

---

## 2. Arquitetura Alvo e Requisitos Técnicos

### 2.1 Padrão de Armazenamento
- **Camada Bronze (Raw):** Dados brutos ingeridos via API/FTP, preservando o formato original (JSON, CSV, Parquet) particionados por data de ingestão.
- **Camada Prata (Trusted/Clean):** Dados limpos, deduplicados, tipados e enriquecidos. Formato preferencial: **Parquet** ou tabelas **Delta Lake / Apache Iceberg**.
- **Camada Ouro (Refined/Analytics):** Modelagem dimensional em **Star Schema** (Tabelas Fato e Dimensão) agregadas para pronta consulta analítica.

### 2.2 Requisitos Funcionais e Não-Funcionais
- **Orquestração:** Uso de ferramenta para agendamento e gerenciamento de DAGs (Prefect, Dagster ou Apache Airflow).
- **Transformação e Qualidade:** Uso de **dbt** ou scripts **PySpark / DuckDB / Polars** com validação automatizada de dados (Great Expectations, dbt tests ou Pandera).
- **Dados Geoespaciais:** Junção de coordenadas ou códigos IBGE de municípios/estados com limites geográficos (GeoJSON / PostGIS / DuckDB Spatial).
- **Camada de Consumo (Serving):** Uma API REST (FastAPI/Flask) ou Engine de Consulta de alta performance (DuckDB/ClickHouse/PostgreSQL) para exposição dos dados modelados.
- **DevOps e Práticas de Software:**
  - Código 100% versionado em repositório Git único.
  - Uso de *Feature Branches* e Pull Requests obrigatoriamente revisados pelo colega de dupla.
  - Containerização integral do ambiente (`docker-compose`).
  - Pipeline de CI/CD (GitHub Actions) validando linting (Ruff/Flake8) e testes unitários.

---

## 3. Guia Detalhado de Fontes de Dados e Acesso

### 3.1 IBGE (Obrigatório)
- **APIs Utilizadas:** 
  - API SIDRA (Agregados demográficos, PIB municipal, Censo, IPCA): `https://apisidra.ibge.gov.br/`
  - API de Malhas Geográficas: `https://servicodados.ibge.gov.br/api/v3/malhas/`
- **Autenticação:** 100% Pública (sem API Key).
- **Desafios de Engenharia:**
  - A API SIDRA possui limite de *payload* por requisição (~100 mil registros por chamada).
  - Exige implementação de estratégias de **paginação/fatiamento por região/ano**, controle de limites de taxa (*rate limiting*) e lógica de retentativas (*backoff* exponencial).

### 3.2 Segunda Fonte de Dados (Escolher 1 para o cruzamento)

#### Opção A — INMET (Clima e Eventos Extremos)
- **API Utilizada:** Portal de Dados Meteorológicos do INMET (`https://apitempo.inmet.gov.br/`).
- **Autenticação:** Pública (sem API Key).
- **Desafios de Engenharia:**
  - Tratamento de medições ausentes ou inválidas (frequentemente preenchidas com valores sentinela como `9999` ou strings vazias).
  - Alinhamento da frequência temporal (dados horários/diários) com a frequência do IBGE (anual/mensal).
  - Cruzamento de coordenadas das estações meteorológicas com os polígonos municipais do IBGE.

#### Opção B — CAGED / MTE (Microdados de Emprego Formal)
- **Fonte Utilizada:** Microdados do CAGED no Portal de Dados Abertos e Servidor FTP/HTTP público do Ministério do Trabalho.
- **Autenticação:** Pública.
- **Desafios de Engenharia:**
  - Arquivos mensais volumosos em lote (CSV/Parquet pesados contendo milhões de movimentações de admissão/demissão).
  - Exige processamento em memória de alto desempenho (DuckDB, PySpark, Polars) e otimização de agregações por setor econômico (CNAE) e código de município.

---

## 4. Planejamento de Sprints e Entregáveis

### Fluxo de Execução das Sprints
1. **Sprint 1:** Alinhamento, Arquitetura, Setup de Infraestrutura e Ingestão Bronze
2. **Sprint 2:** Processamento Camada Prata, Qualidade de Dados e Modelagem Geoespacial
3. **Sprint 3:** Modelagem Ouro (Star Schema), Camada de Consumo e API REST
4. **Sprint 4:** CI/CD, Documentação C4 Model, Testes E2E e Apresentação Final

---

### Sprint 1: Setup do Ambiente, Arquitetura e Ingestão Bronze

#### Objetivos
1. Definir a arquitetura da solução e estabelecer a organização interna da dupla.
2. Subir a infraestrutura básica via Docker.
3. Construir as pipelines de ingestão para a Camada Bronze.

#### Tarefas
- [ ] Criar o repositório no GitHub com guia de contribuição (`CONTRIBUTING.md`), regras de branch (`main`, `develop`) e templates de PR.
- [ ] Mapear as entidades, fluxo de dados e desenhar a arquitetura preliminar.
- [ ] Configurar o arquivo `docker-compose.yml` contendo os serviços da stack (Orquestrador, Banco de Dados / Data Lakehouse, etc.).
- [ ] Desenvolver pipeline de extração da API SIDRA do IBGE com tratamento de limite de chamadas, paginação e salvamento em formato bruto (Bronze).
- [ ] Desenvolver pipeline de extração da segunda fonte de dados (INMET ou CAGED) salvando na Camada Bronze.

#### Critérios de Aceite da Sprint 1
- `docker-compose up` executa todo o ambiente local sem erros.
- Dados brutos do IBGE e da fonte secundária são salvos com sucesso na Camada Bronze, mantendo rastreabilidade por data de ingestão.
- Repositório Git configurado e utilizado por ambos os integrantes via Pull Requests.

---

### Sprint 2: Camada Prata, Qualidade e Tratamento Geoespacial

#### Objetivos
1. Limpar, padronizar e estruturar os dados brutos na Camada Prata.
2. Implementar validações automáticas de qualidade de dados.
3. Unificar códigos territoriais e malhas geográficas.

#### Tarefas
- [ ] Criar pipeline de transformação Bronze -> Prata (limpeza de schema, conversão de tipos de dados, tratamento de nulos/outliers).
- [ ] Implementar suíte de testes de qualidade de dados (verificando nulos, duplicatas, faixas de valores válidas e integridade referencial).
- [ ] Tratar e simplificar dados geográficos do IBGE para permitir junções espaciais eficientes por código de município (IBGE 7 dígitos).
- [ ] Converter os dados limpos para formato colunar otimizado (Parquet / Delta Lake) com estratégia de particionamento adequada (ex: `ano`, `uf`).

#### Critérios de Aceite da Sprint 2
- Dados limpos e padronizados disponíveis na Camada Prata.
- A pipeline falha explicitamente caso os testes de qualidade de dados não passem.
- Mapeamento geográfico funcional relacionando os indicadores da fonte escolhida aos municípios/estados do IBGE.

---

### Sprint 3: Camada Ouro (Modelagem Dimensional) e Camada de Consumo

#### Objetivos
1. Criar o modelo analítico dimensional (Star Schema) na Camada Ouro.
2. Construir a camada de serviço/API para disponibilizar os dados.

#### Tarefas
- [ ] Modelar a Camada Ouro em esquema estrela:
  - **Tabelas Dimensão:** `dim_municipio`, `dim_tempo`, `dim_categoria_economica_climatica`.
  - **Tabela Fato:** `fato_indicadores_socioeconomicos` (cruzando dados de população/PIB do IBGE com métricas do INMET ou CAGED).
- [ ] Automatizar a atualização das tabelas Ouro via orquestrador.
- [ ] Desenvolver uma API REST (FastAPI) com endpoints para consulta de dados agregados (ex: `/api/v1/municipios/{codigo_ibge}/indicadores` ou `/api/v1/ranking-risco`).
- [ ] Implementar índices ou otimizações de consulta na camada de consumo para respostas em milissegundos.

#### Critérios de Aceite da Sprint 3
- Modelo dimensional Ouro criado e populado corretamente.
- A API REST responde a consultas filtradas por período e região com bom desempenho.
- As métricas cruzadas entre IBGE e a fonte escolhida fazem sentido analítico.

---

### Sprint 4: CI/CD, Documentação, Validação e Entrega Final

#### Objetivos
1. Automatizar validações de código e entrega via CI/CD.
2. Documentar a arquitetura e dicionário de dados.
3. Realizar testes de ponta a ponta e preparação da apresentação.

#### Tarefas
- [ ] Configurar GitHub Actions para rodar linter, formatador e testes unitários automaticamente a cada commit/PR.
- [ ] Criar a documentação arquitetural no formato **C4 Model** (Nível 1: Contexto, Nível 2: Contêineres).
- [ ] Gerar e disponibilizar o dicionário de dados de todas as tabelas das camadas Prata e Ouro.
- [ ] Fazer uma rodada completa de teste *End-to-End* (destruir volumes Docker e reconstruir o ambiente do zero via pipeline).
- [ ] Elaborar demonstração prática dos dados e insights gerados pela plataforma.

#### Critérios de Aceite da Sprint 4
- Pipeline de CI/CD rodando e passando em todas as verificações.
- Repositório com documentação clara no `README.md`, contendo instruções de execução, diagrama C4 e dicionário de dados.
- Execução *End-to-End* funcional a partir de um ambiente limpo.

---

## 5. Critérios Globais de Avaliação

| Categoria | Critério | Peso |
| :--- | :--- | :--- |
| **Engenharia de Dados** | Resiliência das pipelines, qualidade das transformações, particionamento e modelagem dimensional (Star Schema). | 35% |
| **Trabalho em Equipe & Git** | Uso de branches, mensagens de commit semânticas, code reviews em Pull Requests e divisão equilibrada de tarefas gerida autonomamente pela dupla. | 25% |
| **Qualidade de Código & DevOps** | Containerização Docker, automação no GitHub Actions, presença de testes automatizados de dados e código. | 20% |
| **Documentação & Arquitetura** | Clareza no `README.md`, diagrama C4 Model, dicionário de dados e facilidade de reprodução do ambiente. | 20% |
