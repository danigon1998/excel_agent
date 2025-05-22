from src.agent_setup import (
    setup_agent,
    run_agent_interaction,
)


from dotenv import load_dotenv

load_dotenv()


def main():
    print("--- Configurando o Agente de Análise de Custos ---")
    try:
        agent_executor = setup_agent()
        print("Agente configurado com sucesso!")
    except ValueError as e:
        print(f"Erro na configuração do agente: {e}")
        print(
            "Por favor, verifique se a variável de ambiente GROQ_API_KEY está definida."
        )
        return
    run_agent_interaction(
        agent_executor,
        # initial_query="Carregue os dados de 'data/input' e me diga o custo total por colaborador. Salvar o resultado",
        # initial_query="Preciso saber o custo total por pessoa para os dados em 'data/input'. Por favor, salve os resultados em um arquivo.",
        initial_query="Pegue os dados da pasta 'data/input', calcule o custo de cada colaborador e me dê um relatório final.",
    )


if __name__ == "__main__":
    main()
