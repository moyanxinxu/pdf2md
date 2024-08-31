# pdf2md

## 环境安装

```bash
conda create -n pdf2md python=3.10
conda activate pdf2md
pip install -r requirements.yml
```

## 文件目录

- src: 源码
  - pdf2md.py: pdf与markdown文件转换器
  - word2md/: word和markdown转换模块
      - word2md.py: word和markdown双向转换器
  - hp_pdf2md.py: 该文件夹下代码超参数
    - order/: 阅读顺序还原相关文件
      - model/: 顺序还原模型文件
      - aux.py: 辅助函数
      - boxes2order.py: 阅读顺序还原模块
      - hp_order.py: 该文件夹下代码超参数
    - ocr/: 光学文字识别模块
      - ocr_imgbyimg.py: 光学文字识别模块
      - hp_ocr.py: 该文件夹下代码超参数
    - others/: pdf与png转换器
      - pdf2imgs.py: pdf与png双向转换器
      - hp_pdf2imgs.py: 该文件夹下代码超参数
