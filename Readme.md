# Agente de Análise de Custos com IA

## 📖 Descrição Breve

Este projeto utiliza inteligência artificial (LLMs via API Groq) para automatizar a leitura, padronização e consolidação de dados de custos de colaboradores a partir de múltiplas planilhas Excel. O objetivo é gerar um relatório final com o custo total por colaborador.

## 🎯 Objetivo Principal

* Automatizar a consolidação de custos de diversas fontes (planilhas de salários, benefícios, ferramentas).
* Lidar com variações nos nomes das colunas das planilhas de entrada usando LLMs.
* Produzir um relatório Excel final com o cálculo do custo por colaborador.

## ⚙️ Pré-requisitos

* Python (recomendado 3.9 ou superior)
* Conta na [GroqCloud](https://console.groq.com/keys) e uma Chave de API (API Key).

## 🚀 Instalação e Configuração

1.  **Clone o Repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_GITHUB]
    cd [NOME_DA_PASTA_DO_PROJETO]
    ```

2.  **Crie e Ative um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv .venv
    # No Windows: .venv\Scripts\activate
    # No macOS/Linux: source .venv/bin/activate
    ```

3.  **Instale as Dependências:**
    O arquivo `requirements.txt` já está incluído no repositório.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure a Chave de API da Groq:**
    * Crie um arquivo chamado `.env` na raiz do seu projeto.
    * Adicione sua chave de API da Groq a este arquivo da seguinte forma:
      ```env
      GROQ_API_KEY=SUA_CHAVE_DE_API_DA_GROQ_AQUI
      ```
    * Substitua `SUA_CHAVE_DE_API_DA_GROQ_AQUI` pela sua chave real.

## ▶️ Como Executar o Projeto

1.  **Prepare suas Planilhas de Entrada:**
    * Coloque os arquivos Excel (`.xlsx`) a serem processados no diretório `data/input/`. (Já temos algumas planilhas como exemplo).

2.  **Execute o Script Principal:**
    No terminal (com o ambiente virtual ativado e na raiz do projeto):
    ```bash
    python main.py
    ```

3.  **Verifique a Saída:**
    * O progresso será exibido no console.
    * O relatório final em Excel será gerado no diretório `data/output/` (o nome exato do arquivo é definido em `main.py`, por exemplo, `relatorio_final_pipeline.xlsx`).

---

## Para mais detalhes, olhar a wiki que esta neste repositorio, onde se encontra a documentação e um video mostrando o que aparece no terminal e o arquivo gerado na pasta output
