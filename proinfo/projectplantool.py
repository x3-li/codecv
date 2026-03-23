from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field, PrivateAttr

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import BaseTool


class ProjectPlanSearchInput(BaseModel):
    """
    LLM が tool を呼び出すときに使用する input schema。

    ここには、LLM から渡させたい parameter だけを定義する。
    retriever や logger のような内部依存はここに書かない。
    """

    query: str = Field(
        ...,
        description=(
            "project 計画書を検索するための自然言語 query。"
            "ユーザーの質問をそのまま長文で渡すのではなく、"
            "vector search に適した簡潔な表現にすること。"
            "例: "
            "'PoC段階の deliverables は何か'、"
            "'この project の milestone を確認したい'、"
            "'risk とその対策を知りたい'"
        ),
    )

    project_name: Optional[str] = Field(
        default=None,
        description=(
            "対象の project 名。"
            "ユーザーが明確に project 名を指定している場合は設定する。"
            "不明な場合は None のままでよい。"
        ),
    )

    top_k: int = Field(
        default=4,
        ge=1,
        le=10,
        description=(
            "取得する candidate chunk の件数。"
            "通常は 3 から 5 程度で十分。"
        ),
    )


class ProjectPlanVectorSearchTool(BaseTool):
    """
    project 計画書向けの vector search tool。

    この tool は、project 計画書、提案書、WBS、milestone 定義、
    risk 管理表、deliverables 一覧などを対象に、
    semantic search を行うために使用する。
    """

    name: str = "project_plan_vector_search"

    description: str = """
project 計画書、提案書、WBS、milestone、risk、deliverables、scope、体制、schedule など、
project 文書に対して semantic search を行う tool。

この tool を使うべき場面:
- ユーザーの質問が project 固有の文書内容に依存している場合
- milestone、deliverables、risk、scope、体制、schedule、予算などを文書から確認したい場合
- 回答前に、project 文書から根拠を取得する必要がある場合

この tool を使わない方がよい場面:
- 一般知識だけで答えられる質問
- 単なる雑談や挨拶
- 文書検索ではなく、すでに与えられた文章の要約や言い換えだけをしたい場合

使用上の注意:
1. query には、vector search に適した簡潔な自然言語を入れること
2. project 名が分かっている場合は、project_name も設定すること
3. 検索結果は根拠情報であり、そのまま盲目的に出力するのではなく整理して使うこと
4. 情報が不足している場合は、不足していると明示し、推測で補わないこと

戻り値:
- content: LLM が読むための要約済み検索結果
- artifact: program 側で利用する raw な検索結果 metadata
""".strip()

    args_schema: type[BaseModel] = ProjectPlanSearchInput
    response_format: str = "content_and_artifact"

    # internal dependency は PrivateAttr で保持する
    _retriever: BaseRetriever = PrivateAttr()
    _index_name: str = PrivateAttr(default="project_plan_index")
    _default_top_k: int = PrivateAttr(default=4)

    def __init__(
        self,
        retriever: BaseRetriever,
        index_name: str = "project_plan_index",
        default_top_k: int = 4,
        **kwargs: Any,
    ) -> None:
        """
        tool の初期化処理。

        Parameters
        ----------
        retriever:
            実際に vector search を実行する BaseRetriever。
            この object は LLM から渡されるのではなく、tool の内部依存として注入する。
        index_name:
            利用中の index 名。artifact や log に含めたい場合に使う。
        default_top_k:
            top_k が未指定だった場合の default 値。
        """
        super().__init__(**kwargs)
        self._retriever = retriever
        self._index_name = index_name
        self._default_top_k = default_top_k

    def _run(
        self,
        query: str,
        project_name: Optional[str] = None,
        top_k: int = 4,
        **kwargs: Any,
    ) -> tuple[str, list[dict[str, Any]]]:
        """
        sync 実行用の method。

        response_format = "content_and_artifact" のため、
        return は (content, artifact) の tuple にする。
        """

        final_top_k = top_k or self._default_top_k

        # retriever 実行
        docs: list[Document] = self._retriever.invoke(query)

        # 必要に応じて project_name filter
        if project_name:
            docs = [
                doc
                for doc in docs
                if (doc.metadata or {}).get("project_name", "").lower() == project_name.lower()
            ]

        docs = docs[:final_top_k]

        if not docs:
            content = (
                "project 計画書から関連情報を取得できませんでした。"
                "project 名、phase 名、deliverables 名などを追加して再検索してください。"
            )
            artifact: list[dict[str, Any]] = []
            return content, artifact

        content_parts: list[str] = []
        artifact: list[dict[str, Any]] = []

        for rank, doc in enumerate(docs, start=1):
            metadata = doc.metadata or {}

            content_parts.append(
                "\n".join(
                    [
                        f"[候補 {rank}]",
                        f"project_name: {metadata.get('project_name', 'unknown')}",
                        f"source: {metadata.get('source', 'unknown')}",
                        f"section: {metadata.get('section', 'unknown')}",
                        f"page: {metadata.get('page', 'unknown')}",
                        f"score: {metadata.get('score', 'unknown')}",
                        f"content: {doc.page_content}",
                    ]
                )
            )

            artifact.append(
                {
                    "rank": rank,
                    "index_name": self._index_name,
                    "page_content": doc.page_content,
                    "metadata": metadata,
                }
            )

        content = (
            "以下は project 計画書から取得した関連 chunk です。"
            "これらを根拠として回答を組み立ててください。"
            "根拠が不十分な場合は、その旨を明示してください。\n\n"
            + "\n\n".join(content_parts)
        )

        return content, artifact

    async def _arun(
        self,
        query: str,
        project_name: Optional[str] = None,
        top_k: int = 4,
        **kwargs: Any,
    ) -> tuple[str, list[dict[str, Any]]]:
        """
        async 実行用の method。

        現時点では sync 版をそのまま利用している。
        retriever 側が async 対応している場合は、ここで await する形に拡張可能。
        """
        return self._run(
            query=query,
            project_name=project_name,
            top_k=top_k,
            **kwargs,
        )