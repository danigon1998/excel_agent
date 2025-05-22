# Projeto de Agente de Análise de Custos

## Ordem de Execução do Projeto

A seguir, a ordem de execução das principais tarefas que guiaram o desenvolvimento deste projeto:

1.  Decidir qual plataforma usar como provedora do modelo a ser escolhido.
2.  Escolher qual modelo de linguagem (LLM) usar.
3.  Criar a estrutura do projeto.
4.  Criar o backlog inicial com as tarefas esperadas do projeto.
5.  Criar funções de carregamento (`load`) e salvamento (`save`) dos arquivos.
6.  Criar o mapeamento de colunas, tanto geral quanto específico por tipo de arquivo.
7.  Documentar o que foi feito e o motivo.

## Por que foi escolhido llama3-70b-8192?

Para o desenvolvimento deste agente capaz de processar arquivos Excel com base em instruções em linguagem natural, a seleção do Modelo de Linguagem (LLM) foi uma decisão técnica fundamental. Dadas as restrições do projeto, incluindo recursos limitados de hardware local (GPU e RAM insuficientes) e um prazo apertado de duas semanas, tornou-se necessário usar um LLM acessível por meio de uma API de nuvem que oferecesse altas velocidades de inferência.

O Groq foi escolhido como plataforma por sua comprovada velocidade de processamento para modelos de linguagem e por fornecer acesso à API para uma variedade de modelos poderosos, mitigando assim as limitações de hardware local. Isso se juntou com o fato de já ter usado esta plataforma anteriormente e ter comprovado sua utilidade.

Entre os modelos de produção disponíveis na Groq, a escolha recaiu no llama3-70b-8192. Essa decisão foi baseada em uma análise que considerou tanto a capacidade intrínseca dos modelos de entender instruções complexas e gerar código relevante, quanto os limites de uso da API (Solicitações por Dia - RPD, Tokens por Dia - TPD) cruciais para permitir a iteração rápida durante o desenvolvimento.

Embora modelos como llama-3.3-70b-versatile (também parâmetros 70B) oferecessem um contexto mais amplo, eles tinham limites diários de RPD e TPD significativamente mais baixos (1000 RPD, 100.000 TPD). Cumprir o prazo de duas semanas exigiu um tempo considerável para vários testes e ajustes, tornando esses limites mais baixos um risco prático.

Em contraste, o llama3-70b-8192 oferece um poderoso recurso de modelo 70B, adequado para entender as complexidades das instruções de manipulação de dados e orientar a geração de código com a biblioteca pandas. Fundamentalmente, seus limites diários (14.400 RPD, 500.000 TPD) são muito mais generosos, fornecendo a flexibilidade necessária para um ciclo de desenvolvimento e teste eficiente, sem interrupções devido a limites de cota.

Embora seus tokens de contexto de 8K sejam menores do que os de outros modelos, eles são considerados suficientes para este caso de uso, em que você interage principalmente com comandos do usuário e metadados de arquivo, em vez de processar o conteúdo completo de tabelas muito grandes diretamente no prompt.

Concluindo, o llama3-70b-8192 foi selecionado por oferecer o equilíbrio ideal entre o poder computacional necessário para a tarefa e os limites de uso da API que melhor se alinham com as restrições de tempo e desenvolvimento do projeto.

## Especificação de Formato de Arquivos de Entrada para o Agente de Análise de Custos

Este documento descreve o formato esperado dos arquivos Excel de entrada (`.xlsx`) que utiliza o Agente de Análise de Custos. É crucial que os arquivos de entrada sigam estas especificações para assegurar o correto processamento e análise dos dados.

### Estrutura de Diretórios Esperada

Os arquivos Excel devem estar localizados dentro da pasta `data/input/` seguindo a seguinte estrutura:
Ótimo! Entendido. Vou compilar tudo isso em formato Markdown, traduzindo as seções adicionais para o Português.
Markdown

# Projeto de Agente de Análise de Custos

## Ordem de Execução do Projeto

A seguir, a ordem de execução das principais tarefas que guiaram o desenvolvimento deste projeto:

1.  Decidir qual plataforma usar como provedora do modelo a ser escolhido.
2.  Escolher qual modelo de linguagem (LLM) usar.
3.  Criar a estrutura do projeto.
4.  Criar o backlog inicial com as tarefas esperadas do projeto.
5.  Criar funções de carregamento (`load`) e salvamento (`save`) dos arquivos.
6.  Criar o mapeamento de colunas, tanto geral quanto específico por tipo de arquivo.
7.  Documentar o que foi feito e o motivo em relação ao mapeamento.
8.  Criar as primeiras "ferramentas" para o agent
9.  Teste de perguntas e prompts

## Por que foi escolhido llama3-70b-8192?

Para o desenvolvimento deste agente capaz de processar arquivos Excel com base em instruções em linguagem natural, a seleção do Modelo de Linguagem (LLM) foi uma decisão técnica fundamental. Dadas as restrições do projeto, incluindo recursos limitados de hardware local (GPU e RAM insuficientes) e um prazo apertado de duas semanas, tornou-se necessário usar um LLM acessível por meio de uma API de nuvem que oferecesse altas velocidades de inferência.

O Groq foi escolhido como plataforma por sua comprovada velocidade de processamento para modelos de linguagem e por fornecer acesso à API para uma variedade de modelos poderosos, mitigando assim as limitações de hardware local. Isso se juntou com o fato de já ter usado esta plataforma anteriormente e ter comprovado sua utilidade.

Entre os modelos de produção disponíveis na Groq, a escolha recaiu no llama3-70b-8192. Essa decisão foi baseada em uma análise que considerou tanto a capacidade intrínseca dos modelos de entender instruções complexas e gerar código relevante, quanto os limites de uso da API (Solicitações por Dia - RPD, Tokens por Dia - TPD) cruciais para permitir a iteração rápida durante o desenvolvimento.

Embora modelos como llama-3.3-70b-versatile (também parâmetros 70B) oferecessem um contexto mais amplo, eles tinham limites diários de RPD e TPD significativamente mais baixos (1000 RPD, 100.000 TPD). Cumprir o prazo de duas semanas exigiu um tempo considerável para vários testes e ajustes, tornando esses limites mais baixos um risco prático.

Em contraste, o llama3-70b-8192 oferece um poderoso recurso de modelo 70B, adequado para entender as complexidades das instruções de manipulação de dados e orientar a geração de código com a biblioteca pandas. Fundamentalmente, seus limites diários (14.400 RPD, 500.000 TPD) são muito mais generosos, fornecendo a flexibilidade necessária para um ciclo de desenvolvimento e teste eficiente, sem interrupções devido a limites de cota.

Embora seus tokens de contexto de 8K sejam menores do que os de outros modelos, eles são considerados suficientes para este caso de uso, em que você interage principalmente com comandos do usuário e metadados de arquivo, em vez de processar o conteúdo completo de tabelas muito grandes diretamente no prompt.

Concluindo, o llama3-70b-8192 foi selecionado por oferecer o equilíbrio ideal entre o poder computacional necessário para a tarefa e os limites de uso da API que melhor se alinham com as restrições de tempo e desenvolvimento do projeto.

## Especificação de Formato de Arquivos de Entrada para o Agente de Análise de Custos

Este documento descreve o formato esperado dos arquivos Excel de entrada (`.xlsx`) que utiliza o Agente de Análise de Custos. É crucial que os arquivos de entrada sigam estas especificações para assegurar o correto processamento e análise dos dados.

### Estrutura de Diretórios Esperada

Os arquivos Excel devem estar localizados dentro da pasta `data/input/` seguindo a seguinte estrutura:

data/
└── input/
├── Ddos Colaboradores.xlsx  # Informação básica dos colaboradores
├── Ferramentas/
│   ├── Ferramenta 1 - Github.xlsx
│   └── Ferramenta 2 - Google Workspace.xlsx
└── Beneficios/
├── Beneficio 1 - Unimed.xlsx
└── Beneficio 2 - Gympass.xlsx

### Formato Esperado por Tipo de Arquivo

A seguir, detalha-se o formato esperado para cada uma das planilhas, incluindo as colunas chave e como são interpretadas.

#### 1. Ddos Colaboradores.xlsx

* **Descrição:** Contém a informação básica dos colaboradores da empresa. É a fonte principal para dados de identificação do pessoal.
* **Colunas Chave Esperadas e sua Interpretação:**
    * `Nome`: Nome completo do colaborador. (Padronizado para: `Nome Colaborador`)
    * `CPF`: Número de identificação do colaborador. (Padronizado para: `CPF Colaborador`)
    * `Departamento`: Departamento ao qual pertence o colaborador. (Padronizado para: `Centro de Custo`)
    * `Salario`: Salário mensal do colaborador. (Padronizado para: `Salario`)
* **Identificação de Uso/Benefício:** Este arquivo define a população base de colaboradores.

#### 2. Ferramenta 1 - Github.xlsx

* **Descrição:** Detalhe dos custos associados ao uso da ferramenta GitHub por colaborador.
* **Colunas Chave Esperadas e sua Interpretação:**
    * `Assinante`: Nome do colaborador que utiliza a ferramenta. (Padronizado para: `Nome Colaborador`)
    * `Documento`: Número de identificação (CPF) do colaborador associado à ferramenta. (Padronizado para: `CPF Colaborador`)
    * `Data Ativacao`: Data de ativação ou início de uso da ferramenta. (Padronizado para: `Data Ativacao Github`)
    * `Copilot`: Custo individual associado ao componente "Copilot" do GitHub (valor numérico). (Padronizado para: `Costo Copilot Github`)
    * `Licença`: Custo individual associado à licença base do GitHub (valor numérico). (Padronizado para: `Costo Licenca Github`)
    * `Valor Mensal`: O custo mensal total pelo uso do GitHub para esse assinante (soma de `Copilot` e `Licença`). (Padronizado para: `Costo Mensal Github`)
* **Identificação de Uso:** Uma linha neste arquivo indica que o `Assinante` (colaborador) está utilizando a ferramenta GitHub.

#### 3. Ferramenta 2 - Google Workspace.xlsx

* **Descrição:** Detalhe dos custos associados ao uso do Google Workspace por colaborador.
* **Colunas Chave Esperadas e sua Interpretação:**
    * `Assinante`: Nome do colaborador que utiliza a ferramenta. (Padronizado para: `Nome Colaborador`)
    * `Documento`: Número de identificação (CPF) do colaborador associado à ferramenta. (Padronizado para: `CPF Colaborador`)
    * `Data Ativacao`: Data de ativação ou início de uso do Google Workspace. (Padronizado para: `Data Ativacao Google Workspace`)
    * `Valor Mensal`: O custo mensal total pelo uso do Google Workspace para esse assinante. (Padronizado para: `Costo Mensal Google Workspace`)
* **Identificação de Uso:** Uma linha neste arquivo indica que o `Assinante` (colaborador) está utilizando o Google Workspace.

#### 4. Beneficio 1 - Unimed.xlsx

* **Descrição:** Informação e custos associados ao benefício de saúde Unimed.
* **Colunas Chave Esperadas e sua Interpretação:**
    * `Código`: Código interno do benefício ou apólice. (Padronizado para: `Codigo Beneficio Unimed`)
    * `Beneficiário`: Nome do beneficiário (que deve ser o `Nome Colaborador` ou um dependente). (Padronizado para: `Nome Colaborador`)
    * `CPF`: Número de identificação (CPF) do colaborador associado ao benefício. (Padronizado para: `CPF Colaborador`)
    * `Tipo`: Tipo de plano ou cobertura da Unimed. (Padronizado para: `Tipo Beneficio Unimed`)
    * `Idade`: Idade do beneficiário. (Padronizado para: `Idade Beneficiario Unimed`)
    * `Dependência`: Tipo de dependência (se aplicável). (Padronizado para: `Dependencia Beneficiario Unimed`)
    * `Data Limite`: Data limite (se aplicável). (Padronizado para: `Data Limite Beneficio Unimed`)
    * `Data Inclusão`: Data de inclusão do beneficiário no plano. (Padronizado para: `Data Inclusao Beneficio Unimed`)
    * `Data Exclusão`: Data de exclusão do beneficiário do plano. (Padronizado para: `Data Exclusao Beneficio Unimed`)
    * `Rubrica`: Categoria ou tipo de gasto. (Padronizado para: `Rubrica Beneficio Unimed`)
    * `Outros`: Outros custos associados (numérico). (Padronizado para: `Outros Custos Beneficio Unimed`)
    * `Total`: O custo mensal total associado a este beneficiário/plano Unimed (comparável ao "Valor Mensal" das ferramentas). (Padronizado para: `Costo Mensal Unimed`)
* **Identificação de Uso:** Uma linha neste arquivo indica que o `Beneficiário` (colaborador ou dependente) está utilizando o benefício Unimed.

#### 5. Beneficio 2 - Gympass.xlsx

* **Descrição:** Informação e custos associados ao benefício Gympass.
* **Colunas Chave Esperadas e sua Interpretação:**
    * `Assinante`: Nome do colaborador que utiliza o benefício. (Padronizado para: `Nome Colaborador`)
    * `Documento`: Número de identificação (CPF) do colaborador associado ao benefício. (Padronizado para: `CPF Colaborador`)
    * `Data Ativacao`: Data de ativação ou início de uso do Gympass. (Padronizado para: `Data Ativacao Gympass`)
    * `Plano`: Tipo de plano do Gympass. (Padronizado para: `Plano Gympass`)
    * `Parcela`: Número de parcela (se o pagamento é fracionado). (Padronizado para: `Parcela Gympass`)
    * `Valor Parcela`: Valor da parcela. (Padronizado para: `Valor Parcela Gympass`)
    * `Coparticipacao`: Valor de coparticipação (se aplicável). (Padronizado para: `Coparticipacion Gympass`)
    * `Valor Desconto`: Valor de desconto aplicado. (Padronizado para: `Valor Desconto Gympass`)
    * `Valor Mensal`: O custo mensal total pelo uso do Gympass para esse assinante. (Padronizado para: `Costo Mensal Gympass`)
* **Identificação de Uso:** Uma linha neste arquivo indica que o `Assinante` (colaborador) está utilizando o benefício Gympass.

---

### Estratégia de Padronização de Nomes de Colunas

Para garantir que o Agente de IA possa processar os dados de maneira consistente e confiável, todos os DataFrames carregados passam por um processo de padronização de nomes de colunas. Este processo segue as seguintes regras:

1.  **Limpeza Inicial:** São removidos espaços em branco no início e no final dos nomes de coluna.
2.  **Mapeamento Específico por Arquivo:** Para cada arquivo, o sistema busca uma palavra-chave em seu nome (ex., "colaboradores", "github", "unimed"). Se uma correspondência for encontrada, um conjunto de regras de mapeamento específicas para aquele tipo de arquivo é aplicado. Isso permite lidar com variações de nomes de coluna que são únicas para uma fonte de dados particular.
3.  **Mapeamento Geral de Fallback:** Se não for encontrado um mapeamento específico para um arquivo, um mapeamento geral que cobre os nomes de coluna mais comuns e seus equivalentes padronizados é aplicado.
4.  **Nomes Padronizados Chave:**
    * **Identificador Único:** `CPF Colaborador` (para `CPF`, `Documento`, `Docuemento`, etc.).
    * **Nome do Colaborador:** `Nome Colaborador` (para `Nome`, `Name`, `Assinante`, `Beneficiário`, etc.).
    * **Custo Mensal Consolidado:** `Costo Mensal [Nome_Fonte]` (ex., `Costo Mensal Github`, `Costo Mensal Unimed`) para o custo total periódico associado a uma ferramenta ou benefício. Isso permite ao agente somar todos os custos mensais de diferentes fontes de maneira unificada.
    * Outros nomes de coluna são padronizados para serem descritivos e consistentes (ex., `Centro de Custo`, `Data Ativacao`).

Assim se assegura que o Agente de IA sempre opere com um esquema de dados previsível e significativo, permitindo-lhe concentrar-se na lógica de análise e resposta às consultas do usuário, em vez de lidar com as inconsistências dos dados de entrada.

### Lógica de Processamento de Dados (Pandas)

Após o carregamento e a padronização dos DataFrames, o Agente de IA, utilizando a biblioteca Pandas, orquestrará as seguintes etapas para analisar e consolidar os custos por colaborador:

#### 1. Unir/Relacionar DataFrames de Ferramentas e Benefícios com o DataFrame Principal de Colaboradores

* **Chave de União:** A chave primária para todas as uniões (`pd.merge`) será a coluna padronizada `CPF Colaborador`. Esta chave garante que cada registro de uso de ferramenta ou benefício seja corretamente associado ao seu respectivo colaborador.
* **Tipo de União:** Será utilizada a operação `pd.merge` com o parâmetro `how='left'`. Isso significa que todos os colaboradores presentes no DataFrame principal (`Dados Colaboradores`) serão mantidos. As informações de ferramentas e benefícios serão adicionadas onde houver correspondência de CPF. Colaboradores que não utilizam uma ferramenta ou benefício específico terão valores `NaN` (Not a Number) nas colunas correspondentes de custo.

#### 2. Calcular o Custo por Colaborador para Cada Ferramenta Específica

* **Identificação de Custos:** Cada DataFrame de ferramenta padronizado terá uma coluna específica para o custo mensal total da ferramenta (`Custo Mensal [Nome_Ferramenta]`, ex: `Custo Mensal Github`, `Custo Mensal Google Workspace`).
* **Agrupamento (se necessário):** Caso haja múltiplas entradas para o mesmo `CPF Colaborador` e a mesma ferramenta (o que pode ocorrer se houver diferentes tipos de licenças ou serviços registrados separadamente, embora já padronizados), o sistema agrupará por `CPF Colaborador` e somará os valores da coluna de custo mensal da ferramenta para obter um custo único por colaborador por ferramenta.
* **"Regras de Rateio":** Para o escopo deste projeto e o prazo de duas semanas, as "regras de rateio" são implementadas diretamente no código Python/Pandas. Isso significa que o valor registrado na coluna `Custo Mensal [Nome_Ferramenta]` (ou a soma dela após o agrupamento) é considerado o custo direto atribuível ao colaborador. O Agente de IA não interpretará regras de rateio complexas dinamicamente a partir de instruções do usuário, mas sim aplicará a lógica já definida no código.

#### 3. Calcular o Custo por Colaborador para Cada Benefício Específico

* **Lógica Idêntica às Ferramentas:** O processo de cálculo do custo por colaborador para cada benefício segue a mesma lógica aplicada às ferramentas. As colunas de custo padronizadas para benefícios (`Custo Mensal [Nome_Beneficio]`, ex: `Custo Mensal Unimed`, `Custo Mensal Gympass`) serão utilizadas, com agrupamento por `CPF Colaborador` e soma dos custos mensais, se necessário.

#### 4. Consolidar Todos os Custos Individuais em Colunas Separadas em um Único DataFrame

* **Fusão Sequencial:** Será realizada uma série de operações `pd.merge(how='left')`, começando com o DataFrame de `Dados Colaboradores` e, em seguida, unindo sequencialmente os DataFrames de cada ferramenta e benefício. Para cada fusão, serão adicionadas apenas as colunas de custo específicas da ferramenta/benefício ao DataFrame consolidado, mantendo a chave `CPF Colaborador`.
* **Estrutura do DataFrame Consolidado:** O resultado será um único DataFrame contendo as informações básicas de cada colaborador e colunas separadas para cada custo individual (ex: `Custo Mensal Github`, `Custo Mensal Google Workspace`, `Custo Mensal Unimed`, `Custo Mensal Gympass`).

#### 5. Calcular o Custo Total por Colaborador

* **Soma das Colunas de Custo:** Uma nova coluna, `Custo Total Colaborador`, será criada no DataFrame consolidado. Esta coluna será o resultado da soma de todas as colunas de custo individual de ferramentas e benefícios (identificadas pelo prefixo `Custo Mensal `). A soma será realizada linha a linha (eixo 1), ignorando valores `NaN` (ou seja, se um colaborador não tiver custo em uma categoria, isso não impedirá a soma das outras categorias).
