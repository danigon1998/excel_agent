from src.agent_setup import setup_agent, run_agent_interaction


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
        initial_query="Carregue os dados de 'data/input' e me diga o custo total por colaborador. Salvar o resultado",
    )


if __name__ == "__main__":
    main()
