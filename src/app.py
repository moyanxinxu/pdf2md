import base64
import os

import gradio as gr

from pdf2md import pdf_md_transformer

model = pdf_md_transformer()


def pdf2base64(file):
    """将PDF文件转换为base64编码的字符串。"""
    if file is None:
        return "从上传PDF文件开始..."
    else:
        pdf_path = file
        try:
            with open(file, "rb") as f:
                encoded_pdf = base64.b64encode(f.read()).decode("utf-8")
            return f"""<iframe src="data:application/pdf;base64,{encoded_pdf}"
                                width="100%"
                                height="800px">
                        </iframe>
                        """
        except Exception as e:
            return f"PDF文件加载失败: {e}"


def update_markdown(pdf_path):
    types, clips = model.predict(pdf_path)
    text_list = model.retrun_md()
    return "\n\n".join(text_list)


with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            output_pdf = gr.HTML("从上传PDF文件开始...")
        with gr.Column():
            with gr.Tab(label="传递PDF文件"):
                input_pdf = gr.File(label="上传PDF文件")
                explorer = gr.FileExplorer(
                    label="选择PDF文件", file_count="single", glob="*.pdf"
                )

            with gr.Tab(label="转化后"):
                with gr.Row():
                    output_md = gr.Markdown(
                        "从上传PDF文件开始...", show_copy_button=True
                    )

    input_pdf.change(pdf2base64, inputs=input_pdf, outputs=output_pdf)
    explorer.change(pdf2base64, inputs=explorer, outputs=output_pdf)
    input_pdf.change(update_markdown, inputs=input_pdf, outputs=output_md)
    explorer.change(update_markdown, inputs=explorer, outputs=output_md)
demo.launch()
