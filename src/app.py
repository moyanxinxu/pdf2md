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
    text_list = model.clean_text(types, clips)

    return "\n\n".join(text_list)


def translate(current_language, target_language, text):
    return model.translate(current_language, target_language, text)


with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            output_pdf = gr.HTML("从上传PDF文件开始...")
        with gr.Column():
            with gr.Tab(label="PDF to Markdown"):
                input_pdf = gr.File(label="上传PDF文件")

                output_md = gr.TextArea(
                    placeholder="从上传PDF文件开始...",
                    show_copy_button=True,
                    interactive=True,
                    label="转换结果",
                )
                transform_btn = gr.Button("开始转换")
            with gr.Tab(label="翻译"):
                with gr.Row():
                    current_dropbox = gr.Dropdown(
                        ["en", "zh"],
                        value="en",
                        label="当前语言",
                    )
                    target_dropbox = gr.Dropdown(
                        ["en", "zh"], value="zh", label="目标语言"
                    )
                input_text = gr.TextArea(label="输入文本")
                output_text = gr.TextArea(label="翻译结果")
                translate_btn = gr.Button("开始翻译")

    input_pdf.change(pdf2base64, inputs=input_pdf, outputs=output_pdf)

    # update the markdown text
    transform_btn.click(update_markdown, inputs=input_pdf, outputs=output_md)
    translate_btn.click(
        translate,
        inputs=[current_dropbox, target_dropbox, input_text],
        outputs=output_text,
    )

demo.launch()
