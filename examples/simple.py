import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from browser_use import Agent

load_dotenv()

# Carregar variáveis do .env
load_dotenv()
EMAIL = os.getenv("EMAIL")
SENHA = os.getenv("SENHA")

# Initialize the model
llm = ChatOpenAI(
	model='gpt-4o-mini',
	temperature=0.0,
)

task = f"""
você vai acessar https://asimov.academy/.
depois você vai clicar em "entrar" e escrever {EMAIL} e a senha "{SENHA}". 
vai acessar na esquerda o menu lateral e clicar em "cursos".
vai acessar o curso Introdução à Lógica de Programação.
vai acessar o vídeo 'O Conceito de Algoritmo' e assistir por 5 segundos.
"""

agent = Agent(task=task, llm=llm)


async def main():
	await agent.run()


if __name__ == '__main__':
	asyncio.run(main())





# """
# pesquise na web sites que vendam esses produtos e encontre os melhores preços. 
# Ao final crie uma tabela com o nome do item o link do site com menor valor e o valor. e some o valor total dos itens.

# Fonte - Cooler Master MWE 750W, 80 Plus Bronze
# Placa de Vídeo - MSI RTX 3050 Ventus 2X XS OC NVIDIA GeForce, 8GB GDDR6
# Processador - AMD Ryzen 7 5700, 8-Core, 16-Threads, 3.7GHz (4.6GHz Turbo), Cache 20MB
# Cooler para Processador - DeepCool High Performance AK400, 120mm, Intel-AMD
# Gabinete Gamer - Rise Mode Glass 06X, Mid Tower, ATX, Lateral em Vidro Fumê e Frontal em Vidro Temperado
# Memória RAM - Kingston Fury Beast, 16GB (2x8GB), 3600MHz, DDR4, CL17
# SSD - Kingston NV2, 1TB, M.2 NVMe, 2280, Leitura 3500MB/s e Gravação 2100MB/s
# Placa-Mãe - MSI B550M PRO-VDH, Chipset B550, AMD AM4, mATX, DDR4
# """