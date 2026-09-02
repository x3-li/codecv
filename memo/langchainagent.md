import asyncio
import chainlit as cl


@cl.on_message
async def on_message(user_message: cl.Message):

    stream = await agent.astream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message.content,
                }
            ]
        },
        version="v3",
    )

    answer: cl.Message | None = None

    async def consume_model_message(model_stream):

        nonlocal answer

        async def reasoning_worker():

            reasoning_iter = model_stream.reasoning.__aiter__()

            try:
                first_token = await anext(reasoning_iter)
            except StopAsyncIteration:
                return

            async with cl.Step(
                name="AI Thinking",
                type="llm",
            ) as thinking_step:

                await thinking_step.stream_token(
                    first_token
                )

                async for token in reasoning_iter:
                    await thinking_step.stream_token(
                        token
                    )

        async def text_worker():

            nonlocal answer

            async for token in model_stream.text:

                if answer is None:
                    answer = cl.Message(
                        content="",
                        author="AI",
                    )
                    await answer.send()

                await answer.stream_token(token)

        await asyncio.gather(
            reasoning_worker(),
            text_worker(),
        )

        # 完整 AIMessage
        full_message = await model_stream.output

        return full_message

    async for model_stream in stream.messages:

        await consume_model_message(
            model_stream
        )

    # Agent 最终 state
    final_state = await stream.output

    if answer is not None:
        await answer.update()