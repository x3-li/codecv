import os
import shutil
from pathlib import Path
from typing import List

from pypdf import PdfReader, PdfWriter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


# =========================
# 設定
# =========================

PDF_PATH = "input.pdf"
OUTPUT_FILE = "output.txt"
TMP_DIR = "tmp_batches"

INITIAL_BATCH_SIZE = 50
MIN_BATCH_SIZE = 1

MODEL_NAME = "gemini-1.5-pro"


# =========================
# ディレクトリ操作
# =========================

def recreate_dir(path: str):
    """ディレクトリを削除して再作成"""
    p = Path(path)
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)


def cleanup_tmp(path: str):
    """tmpディレクトリ削除"""
    p = Path(path)
    if p.exists():
        shutil.rmtree(p)


# =========================
# PDF分割処理
# =========================

def split_pdf(input_pdf: str, batch_size: int, output_dir: str) -> List[str]:
    """
    PDFを batch_size ページごとに分割する
    """
    recreate_dir(output_dir)

    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)

    files = []
    index = 0

    for start in range(0, total_pages, batch_size):

        end = min(start + batch_size, total_pages)

        writer = PdfWriter()

        for page in range(start, end):
            writer.add_page(reader.pages[page])

        file_path = Path(output_dir) / f"batch_{index}.pdf"

        with open(file_path, "wb") as f:
            writer.write(f)

        files.append(str(file_path))
        index += 1

    return files


# =========================
# LLM初期化
# =========================

def build_llm():
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0
    )


# =========================
# LLM文字抽出
# =========================

def extract_text(llm, pdf_file: str):

    prompt = """
以下のPDFファイルから、すべての文字情報を抽出してください。

要求：
1. ページ順に出力すること
2. 要約せず原文を可能な限りそのまま出力
3. タイトル、本文、表、脚注なども可能な限り含める
4. 出力形式はプレーンテキスト
"""

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "media",
                "mime_type": "application/pdf",
                "file_path": pdf_file
            }
        ]
    )

    result = llm.invoke([message])

    return result.content


# =========================
# batch処理
# =========================

def process_pdf(input_pdf: str, batch_size: int):

    llm = build_llm()

    batch_files = split_pdf(
        input_pdf,
        batch_size,
        TMP_DIR
    )

    outputs = []

    for file in batch_files:

        print("processing:", file)

        text = extract_text(llm, file)

        outputs.append(text)

    return "\n".join(outputs)


# =========================
# メイン処理
# =========================

def main():

    batch_size = INITIAL_BATCH_SIZE

    while batch_size >= MIN_BATCH_SIZE:

        try:

            print("batch_size:", batch_size)

            result = process_pdf(
                PDF_PATH,
                batch_size
            )

            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(result)

            cleanup_tmp(TMP_DIR)

            print("complete")

            return

        except Exception as e:

            print("failed:", e)

            cleanup_tmp(TMP_DIR)

            if batch_size == 1:
                break

            batch_size = batch_size // 2

    raise RuntimeError("all retries failed")


if __name__ == "__main__":
    main()