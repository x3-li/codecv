import logging

import chainlit as cl

from langchain_core.messages import (
    AIMessageChunk,
    HumanMessage,
    ToolMessage,
)

logger = logging.getLogger(__name__)


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """
    ユーザーメッセージ受信 → Agent を astream で呼び出す。

    UI 表示順：
        User
        ↓
        Thinking
        ↓
        Tool
        ↓
        Thinking
        ↓
        AI Answer
    """

    agent = _get_agent()

    # ==========================================
    # Message History
    # ==========================================
    message_history: list = cl.user_session.get(
        "message_history",
        [],
    )

    message_history.append(
        HumanMessage(content=message.content)
    )

    # ==========================================
    # UI 状態
    # ==========================================

    # 最終回答
    # ここでは send() しない。
    # 最初の text token が来た時に stream_token() で表示開始する。
    answer = cl.Message(content="")

    # 現在の reasoning
    reasoning_buffer = ""

    # 現在 UI に表示中の Thinking Step
    thinking_step: cl.Step | None = None

    # Agent の最終 state
    final_state = None

    # ==========================================
    # Thinking 処理
    # ==========================================

    async def append_reasoning(reasoning: str) -> None:
        """
        reasoning を追加する。

        最初の reasoning が届いた瞬間に Thinking Step を send() し、
        UI 上の表示位置を先に確保する。
        """
        nonlocal reasoning_buffer
        nonlocal thinking_step

        if not reasoning:
            return

        # 最初の reasoning token が来た瞬間に
        # Thinking Step を UI に作成する
        if thinking_step is None:
            thinking_step = cl.Step(
                name="Thinking",
                type="llm",
                default_open=False,
            )

            # ★重要
            # 内容が完成するまで待たず、ここですぐ send する。
            # これによって Tool Step より前の位置を確保する。
            await thinking_step.send()

        reasoning_buffer += reasoning

    async def flush_reasoning() -> None:
        """
        現在蓄積している reasoning を確定し、
        Thinking Step を update する。
        """
        nonlocal reasoning_buffer
        nonlocal thinking_step

        if thinking_step is None:
            return

        thinking_step.output = reasoning_buffer

        # 既に send 済みなので、
        # 新しい Step を作らず既存 Step を更新する。
        await thinking_step.update()

        # 次の reasoning 用にリセット
        reasoning_buffer = ""
        thinking_step = None

    # ==========================================
    # Agent Stream
    # ==========================================

    try:
        async for mode, chunk in agent.astream(
            {
                "messages": message_history,
            },
            stream_mode=[
                "messages",
                "values",
            ],
        ):

            # ==================================
            # State Update
            # ==================================

            if mode == "values":
                final_state = chunk
                continue

            # stream_mode="messages"
            msg_chunk, metadata = chunk

            # ==================================
            # Tool Result
            # ==================================

            if isinstance(msg_chunk, ToolMessage):

                # 通常は Tool Call を検出した時点で
                # reasoning は flush 済み。
                #
                # 念のため ToolMessage 到着時にも
                # flush しておく。
                await flush_reasoning()

                continue

            # ==================================
            # AIMessageChunk 以外は無視
            # ==================================

            if not isinstance(msg_chunk, AIMessageChunk):
                continue

            # ==================================
            # 1. Reasoning
            # ==================================

            reasoning = _extract_reasoning(msg_chunk)

            if reasoning:
                await append_reasoning(reasoning)

            # ==================================
            # 2. Tool Call
            # ==================================
            #
            # ToolMessage を待ってはいけない。
            #
            # ToolMessage が来る時点では、
            # Tool は既に実行済み。
            #
            # AI が Tool を呼び出そうとした瞬間に
            # Thinking を確定する。
            # ==================================

            tool_calls = getattr(
                msg_chunk,
                "tool_calls",
                None,
            )

            tool_call_chunks = getattr(
                msg_chunk,
                "tool_call_chunks",
                None,
            )

            has_tool_call = bool(
                tool_calls
                or tool_call_chunks
            )

            if has_tool_call:

                # ★重要
                # 実際の Tool が開始する前に
                # Thinking Step を完成させる
                await flush_reasoning()

                continue

            # ==================================
            # 3. Final Answer Text
            # ==================================

            text = _extract_text(msg_chunk)

            if text:

                # Final Answer が始まったということは、
                # その直前までの reasoning は終了。
                await flush_reasoning()

                # AI Answer をストリーミング表示
                await answer.stream_token(text)

    except Exception as exc:  # noqa: BLE001

        logger.exception(
            "Agent 実行エラー"
        )

        # 途中まで Thinking が存在する場合は確定
        await flush_reasoning()

        error_text = (
            f"Agent 実行エラー: {exc}"
        )

        if answer.content:
            await cl.Message(
                content=error_text
            ).send()
        else:
            answer.content = error_text

    finally:

        # ======================================
        # 残った reasoning を確定
        # ======================================

        await flush_reasoning()

        # ======================================
        # Final Answer 確定
        # ======================================

        if answer.content:
            await answer.update()

    # ==========================================
    # Message History Update
    # ==========================================

    if final_state:
        cl.user_session.set(
            "message_history",
            final_state["messages"],
        )
    else:
        cl.user_session.set(
            "message_history",
            message_history,
        )