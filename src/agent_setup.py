import os
import pandas as pd
from pathlib import Path

from langchain_groq import ChatGroq  # ChatGroq para poder usar o modelo Llama3-70b
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent

from src.data_handler import load_excel_files, save_dataframe_to_excel
from src.data_processor import perform_full_cost_analysis

_GLOBAL_LOADED_DATAFRAMES = {}
_GLOBAL_PROCESSED_DATAFRAME = None


SYSTEM_PROMPT = """
Você é um agente de análise de custos que entende solicitações em linguagem natural e executa ferramentas passo a passo para realizar cálculos sobre dados organizacionais.

Seu objetivo principal é ajudar o usuário a entender e analisar custos por colaborador, com base em arquivos como planilhas de salários, benefícios e ferramentas. Sempre que possível, você deve executar ferramentas de maneira precisa, explicando seu raciocínio antes de agir.

Aqui está um exemplo de como você deve pensar e agir:

Exemplo:
Usuário: Preciso saber o custo total por pessoa para os dados em 'data/input'. Por favor, salve os resultados em um arquivo.

Pensamento: O usuário quer que eu carregue os dados, analise os custos por pessoa e salve o resultado.

Ação: load_data

Observação: Dados carregados com sucesso.

Pensamento: Agora preciso calcular os custos por pessoa.

Ação: analyze_and_calculate_all_costs

Observação: Análise de custos concluída.

Pensamento: O usuário pediu para salvar os resultados, então agora devo executar a ferramenta de salvamento.

Ação: save_processed_data

Observação: Arquivo salvo em 'data/output/relatorio_final.xlsx'.

Pensamento: A tarefa foi concluída com sucesso.

--- Fim do exemplo ---

A cada nova solicitação, pense passo a passo. Use ferramentas apenas quando fizer sentido. 
Se o usuário pedir para salvar, gere o arquivo após a análise.
"""


@tool
def load_data(input_dir: str):
    """
    Carrega todos os arquivos Excel (.xlsx) de um diretório especificado
    (e seus subdiretórios) e os padroniza.
    Retorna um dicionário onde as chaves são os nomes padronizados dos arquivos (ex: 'ddos colaboradores')
    e os valores são os DataFrames do Pandas correspondentes.
    Use esta ferramenta como o PRIMEIRO PASSO para obter os dados.
    Argumentos:
        input_dir (str): O caminho para o diretório raiz dos arquivos Excel.
                         Ex: 'data/input'.
    """
    print(f"\n[Tool Call] Chamando load_data para o diretório: {input_dir}")
    path_obj = Path(input_dir)
    loaded_dfs = load_excel_files(path_obj)

    if not loaded_dfs:
        return "Nenhum arquivo Excel encontrado ou carregado no diretório específico"

    global _GLOBAL_LOADED_DATAFRAMES
    _GLOBAL_LOADED_DATAFRAMES = loaded_dfs

    summary_message = (
        f"Dados carregados com sucesso do diretório '{input_dir}'. "
        f"Foram encontrados e processados {len(loaded_dfs)} DataFrames: "
        f"{', '.join(loaded_dfs.keys())}. "
        "Os dados estão prontos para análise."
    )

    return summary_message


@tool
def analyze_and_calculate_all_costs():
    """
    Realiza a análise completa de custos. Este processo inclui:
    1. Consolidar DataFrames de colaboradores, ferramentas e benefícios em um único DataFrame.
    2. Calcular o custo mensal para cada ferramenta/benefício por colaborador.
    3. Calcular o custo TOTAL por colaborador somando todos os custos individuais.
    Esta ferramenta deve ser usada APÓS 'load_data' ter carregado os DataFrames.
    Retorna um DataFrame do Pandas que contém todas as informações de colaboradores
    e as colunas de custo consolidadas, incluindo 'Costo Total Colaborador'.
    Argumentos:
        loaded_dataframes (dict): O dicionário de DataFrames retornado pela ferramenta 'load_data'.
    """
    print(f"\n[Tool Call] Chamando analyze_and_calculate_all_costs")
    global _GLOBAL_LOADED_DATAFRAMES
    global _GLOBAL_PROCESSED_DATAFRAME

    if not _GLOBAL_LOADED_DATAFRAMES:
        return (
            "Erro: Nenhum DataFrame carregado. Por favor, execute 'load_data' primeiro."
        )

    result_df = perform_full_cost_analysis(_GLOBAL_LOADED_DATAFRAMES)

    if result_df.empty:
        _GLOBAL_PROCESSED_DATAFRAME = pd.DataFrame()
        return "A análise de custos não produziu resultados. O DataFrame consolidado está vazio."

    _GLOBAL_PROCESSED_DATAFRAME = result_df

    return (
        "Análise de custos concluída. O custo total por colaborador foi calculado. "
        "As primeiras 3 linhas do DataFrame resultante são:\n"
        + result_df.head(3).to_markdown(index=False)
    )


@tool
def save_processed_data(output_path: str):
    """
    Salva um DataFrame do Pandas em um arquivo Excel (.xlsx) no caminho especificado.
    Esta ferramenta é útil para persistir resultados de análises.
    Argumentos:
        df (pd.DataFrame): O DataFrame a ser salvo.
        output_path (str): O caminho completo, incluindo o nome do arquivo, onde o DataFrame será salvo.
                           Ex: 'data/output/relatorio_final.xlsx'.
    Retorna o caminho do arquivo salvo em caso de sucesso, ou uma mensagem de erro.
    """
    print(f"\n[Tool Call] Chamando save_processed_data para o arquivo: {output_path}")

    global _GLOBAL_PROCESSED_DATAFRAME
    if _GLOBAL_PROCESSED_DATAFRAME is None or _GLOBAL_PROCESSED_DATAFRAME.empty:
        return "Erro: Nenhum DataFrame processado para salvar. Execute 'analyze_and_calculate_all_costs' primeiro."
    path_obj = Path(output_path)
    saved_path = save_dataframe_to_excel(_GLOBAL_PROCESSED_DATAFRAME, path_obj)
    if saved_path is None:
        return f"Erro ao salvar o DataFrame em {output_path}."

    return f"DataFrame salvo com sucesso em {saved_path}"


def setup_llm():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "A variável de ambiente GROQ_API_KEY não está definida. "
            "Certifique-se de que o arquivo .env esteja na raiz do projeto "
            "e que load_dotenv() seja chamado no main.py."
        )
    llm = ChatGroq(
        temperature=0, groq_api_key=groq_api_key, model_name="llama3-8b-8192"
    )
    return llm


def setup_agent(debug=False):
    llm = setup_llm()
    tools = [load_data, analyze_and_calculate_all_costs, save_processed_data]

    # Definição do prompt para guiar o agente criado
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=debug,
        handle_parsing_errors=True,
    )
    return agent_executor


def run_agent_interaction(agent_executor: AgentExecutor, initial_query: str = None):
    if initial_query:
        print(f"Executando interação com a query inicial: {initial_query}")
        response = agent_executor.invoke({"input": initial_query})
        print("Relatorio gerado com sucesso!!!")
    else:
        print("Agente pronto para interagir. Digite 'sair' para encerrar.")
        while True:
            user_input = input("Você: ")
            if user_input.lower() == "sair":
                print("Encerrando a interação.")
                break
            try:
                response = agent_executor.invoke({"input": user_input})
                print("Resposta do Agente")
                print(response["output"])
            except Exception as e:
                print(f"Erro ao processar a entrada do usuário: {e}")
                print("Por favor, tente reformular sua pergunta ou tente novamente.")
