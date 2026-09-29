## Guia de contribuição - Plataforma de Inteligencia Territorial

Para garantir a organização e a qualidade do projeto, todos os integrantes devem seguir este fluxo:

## 1. Estrutura de Branches
* `main`: Código final, testado e estável.
* `develop`: Branch principal de desenvolvimento.
* `feature/<nome-da-tarefa>`: Branches temporárias para desenvolvimento de novas tarefas.

## 2. Fluxo de trabalho
1. Escolha uma Issue no kanban e mova para "In Progress".
2. Crie uma branch a partir da `develop`(ex: `feature/ingestao-ibge`).
3. Desenvolva e faça commits claros (ex: `feat: adiciona estrator da API SINDRA`).
4. Abra um **Pull Request (PR)** da sua branch para a `develop`.
5. A dupla deve revisar o código. **Não permitido fazer um merge do próprio PR sem aprovação.**