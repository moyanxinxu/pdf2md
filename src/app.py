import base64

import gradio as gr

from pdf2md import pdf_md_transformer

model = pdf_md_transformer()

def pdf2base64(file):
    """将PDF文件转换为base64编码的字符串。"""
    if file is None:
        return "从上传PDF文件开始..."
    else:
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
            input_pdf = gr.File(label="上传PDF文件")

            transform_btn = gr.Button("开始转换")

            output_md = gr.TextArea(
                placeholder="从上传PDF文件开始...",
                show_copy_button=True,
                interactive=True,
                label="转换结果",
            )

    input_pdf.change(pdf2base64, inputs=input_pdf, outputs=output_pdf)

    # update the markdown text
    transform_btn.click(update_markdown, inputs=input_pdf, outputs=output_md)

demo.launch()
