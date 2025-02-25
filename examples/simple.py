import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from browser_use import Agent

load_dotenv()

# Initialize the model
llm = ChatOpenAI(
	model='gpt-4o-mini',
	temperature=0.0,
)
task = 'Encontre informações atuais dos meus concorrentes Arco, Songz, VMG Aires, e Sanz Clima, quero saber dos lançamentos e inovações'

agent = Agent(task=task, llm=llm)


async def main():
	await agent.run()


if __name__ == '__main__':
	asyncio.run(main())
