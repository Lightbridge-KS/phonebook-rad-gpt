# from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl

from _utils import read_markdown_file


@cl.on_chat_start
async def on_chat_start():
    model_openai = ChatOpenAI(model="gpt-4o-mini", streaming=True)
    # model_anthropic = ChatAnthropic(model='claude-3-haiku-20240307', streaming=True) # stream=True
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                read_markdown_file("prompt/phone-pr.md"),
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model_openai | StrOutputParser()
    cl.user_session.set("runnable", runnable)



@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Quick Start",
            message="Who are you and how do I use you?",
            icon="/public/lightbulb.svg",
            ),
        cl.Starter(
            label="Ex: CTER",
            message="CTER",
            icon="/public/pen.svg",
        ),
        cl.Starter(
            label="Ex: 7SW",
            message="7SW",
            icon="/public/pen.svg",
        ),
        ]
# ...


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
