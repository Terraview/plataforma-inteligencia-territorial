# Documentação de Arquitetura e Fluxo de Dados — Sprint 1

## 1. Fontes de Dados Selecionadas

- **Fonte Primária (Obrigatória):**
  - IBGE — API SIDRA para dados de PIB e Demografia.
  - API de Malhas Geográficas do IBGE.

- **Fonte Secundária:**
  - [Preencher: INMET — Dados Meteorológicos ou CAGED — Microdados de Emprego]

---

## 2. Entidades Principais e Chaves de Ligação

### Município (IBGE)

- **Código IBGE:** código de 7 dígitos do município (`codigo_ibge`)
- **Nome:** nome do município
- **UF:** unidade federativa
- **Região:** região geográfica

### Indicadores Socioeconômicos (IBGE)

- **Ano**
- **PIB municipal**
- **População estimada**

### Métricas da Fonte Secundária

#### Se INMET

- Código do município/estação
- Data/Hora
- Temperatura média
- Precipitação acumulada

#### Se CAGED

- Código do município
- Mês/Ano
- Saldo de movimentações:
  - Admissões
  - Desligamentos
- Setor CNAE

### Chave Primária de Cruzamento

O cruzamento dos dados será realizado utilizando:

- **Código IBGE de 7 dígitos do município**
- **Período temporal (Ano/Mês)**

---

## 3. Fluxo de Dados pelas Camadas — Medallion Architecture

### 3.1. Camada Bronze — Raw

Responsável pelo armazenamento dos dados brutos, preservando o formato original das fontes.

- Arquivos armazenados no formato original:
  - JSON
  - CSV
- Particionamento por data de ingestão:
  - `data_ingestao=YYYY-MM-DD`
- Os dados são mantidos sem transformações significativas, permitindo rastreabilidade e reprocessamento.

### 3.2. Camada Prata — Trusted

Responsável pela limpeza, padronização e validação dos dados provenientes da camada Bronze.

- Limpeza dos dados
- Conversão e padronização de tipos
- Deduplicação
- Tratamento de valores nulos
- Padronização de nomes e estruturas
- Exportação em formato colunar otimizado:
  - **Parquet**

### 3.3. Camada Ouro — Analytics

Responsável pela modelagem dos dados preparados para análise e consumo.

Será utilizado um modelo dimensional baseado em **Star Schema**, composto por:

- **Tabela fato:**
  - `fato_indicadores_socioeconomicos`

- **Dimensões:**
  - `dim_municipio`
  - `dim_tempo`

Essa camada concentrará os dados consolidados e prontos para análises, indicadores e consultas.

### 3.4. Camada de Consumo

Responsável pela disponibilização dos dados para aplicações e consumidores externos.

- Exposição dos dados por meio de **API REST**
- Framework utilizado:
  - **FastAPI**

A API permitirá consultar os indicadores socioeconômicos e demais informações disponibilizadas pela camada Ouro.