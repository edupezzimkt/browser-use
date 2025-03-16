import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent
from browser_use.agent.views import AgentHistoryList
from langchain_ollama import ChatOllama

# modelos gemma3:27b  llama3.1:8b deepseek-r1:14b

# Carregar variáveis do .env
load_dotenv()
EMAIL = os.getenv("EMAIL")
SENHA = os.getenv("SENHA")

# Definir a tarefa usando as credenciais protegidas
task = f"""
você vai acessar https://asimov.academy/.
depois você vai clicar em "entrar" e escrever {EMAIL} e a senha "{SENHA}". 
vai acessar na esquerda o menu lateral e clicar em "cursos".
vai acessar o curso Introdução à Lógica de Programação.
vai acessar o vídeo 'O Conceito de Algoritmo' e assistir por 5 segundos.
"""

task1 = """ você é um analista de marketing e vai acessar https://www.google.com.br/ 
sua tarefa é coletar informações e novidades sobre meus concorrentes que são: Aquamotion, Mundo a Vapor, Snowland e Alpen Park.
Você vai pesquisar em sites de notícias e redes sociais e trazer as informações mais relevantes sobre cada um deles.

Você vai trazer principais insights e fazer um relatório em markdown de até 500 palavras para a direção da empresa. 
"""

async def run_search() -> AgentHistoryList:
    agent = Agent(
        task=task,
        llm=ChatOllama(
            model="llama3.1:8b",
            num_ctx=32000,
        ),
    )

    result = await agent.run()
    return result


async def main():
    result = await run_search()
    print("\n\n", result)


if __name__ == "__main__":
    asyncio.run(main())
