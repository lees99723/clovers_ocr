import os
from paddleocr import PaddleOCRVL


os.environ['FLAGS_use_onednn'] = '0'

pipeline = PaddleOCRVL(device="cpu", use_layout_detection=False)

output = pipeline.predict("C:\OCR_test\ocr_test1\00000222.jpg")

# 3. 결과 출력 및 저장 (주신 코드 로직 그대로)
for res in output:
    res.print() ## 打印预测的结构化输出
    res.save_to_json(save_path="C:\OCR_test\ocr_test1\output") ## 保存当前图像的结构化json结果
    res.save_to_markdown(save_path="C:\OCR_test\ocr_test1\output") ## 保存当前图像的markdown格式的结果