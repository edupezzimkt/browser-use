import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from browser_use import Agent
from browser_use.agent.views import ActionResult
from browser_use.controller.service import Controller

load_dotenv()

# Initialize the model
llm = ChatOpenAI(
	model='gpt-4o',
	temperature=0.0,
)
controller = Controller()


task = "Acesse o site da https://www.snowland.com.br/ingressos/, feche a popup. escola o dia de amanhã no calendário, depoi clique em pesquisar ingressos. após esta ação vai carregar os produtos eu quero como objetivo: pegar o nome e o preço de todos os ingressos que contêm na página."

agent = Agent(task=task, llm=llm, controller=controller)


async def main():
	await agent.run()

	# new_task = input('Type in a new task: ')
	new_task = 'Encontre os ingressos e o valor'

	agent.add_new_task(new_task)

	await agent.run()


if __name__ == '__main__':
	asyncio.run(main())
