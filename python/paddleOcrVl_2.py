# 글 삽입까지, 
# predict 함수 -> 좌표가 부정확
# PyMuPDF는 글자의 밑줄을 기준으로 잡음/predict는 텍스트 박스 높이의 75%지점을 기준으로 잡음 -> 실제이미지와 텍스트의 위치가 어긋남

import os
import fitz  # PyMuPDF
from paddleocr import PaddleOCRVL
from PIL import Image

def create_searchable_pdf_with_fitz(image_path, output_pdf_path):
    print("⏳ 엔진 초기화 및 이미지 분석 중...")
    ocr = PaddleOCRVL(
        device="gpu", 
        use_layout_detection=True,
        use_doc_orientation_classify=False, # True 했을 때 앵글이 180도 돌아가버림
        use_doc_unwarping=True,
        use_ocr_for_image_block=False 
    )
    
    img = Image.open(image_path)
    img_w, img_h = img.size
    
    # PDF 스케일 계산
    max_h, max_w = 650.0, 450.0
    scaling_factor = min(max_w / img_w, max_h / img_h)
    pdf_w, pdf_h = img_w * scaling_factor, img_h * scaling_factor

    doc = fitz.open()
    page = doc.new_page(width=pdf_w, height=pdf_h) 
    page.insert_image(page.rect, filename=image_path)
    
    font_path = "C:/Windows/Fonts/malgun.ttf"
    if not os.path.exists(font_path):
        # 맑은 고딕이 없을 경우 대비 (윈도우 기본 폰트 경로)
        font_path = "C:/Windows/Fonts/batang.ttc" 
        
    page.insert_font(fontname="ko", fontfile=font_path)

    # OCR 수행
    results = ocr.predict(image_path, format_block_content=False) 
    
    layout_boxes = results[0]['layout_det_res']['boxes']
    parsing_res = results[0]['parsing_res_list']
    
    print(f"🔎 총 {len(layout_boxes)}개의 블록을 매칭합니다.")
    print(results[0])

    # 좌표와 텍스트 매칭 루프
    for i, (box, p_item) in enumerate(zip(layout_boxes, parsing_res)):
        coords = box['coordinate']
        x1, y1, x2, y2 = [c * scaling_factor for c in coords]
        box_h = y2 - y1
        
        # 텍스트 추출 (딕셔너리/객체 모두 대응)
        if isinstance(p_item, dict):
            content = p_item.get('block_content') or p_item.get('content', '')
        else:
            content = getattr(p_item, 'block_content', '') or getattr(p_item, 'content', '')

        if not content or not content.strip():
            continue

        lines = content.split('\n')
        line_count = len(lines)
        line_height = box_h / line_count if line_count > 0 else box_h
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            
            # y 좌표 계산
            current_y = y1 + (idx * line_height) + (line_height * 0.75)
            
            # 폰트 크기 결정
            f_size = max(6, min(line_height * 0.8, 11))
            
            try:
                page.insert_text(
                    (x1, current_y), 
                    line, 
                    fontsize=f_size, 
                    fontname="ko",  # 위에서 등록한 'ko' 사용
                    render_mode=0    # 우선 글자가 보이나 확인 (확인 후 3으로 변경)
                )
            except Exception as e:
                print(f"❌ [블록{i}-줄{idx}] 삽입 실패: {e}")

    # 저장
    output_dir = os.path.dirname(output_pdf_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    doc.save(output_pdf_path)
    doc.close()
    print(f"\n🏁 생성 완료: {output_pdf_path}")

if __name__ == "__main__":
    base_dir = r"C:\OCR_test\ocr_test1"
    image_file = os.path.join(base_dir, "00000006.jpg")
    output_pdf = os.path.join(base_dir, "output", "00000006반전.pdf")
    
    if os.path.exists(image_file):
        create_searchable_pdf_with_fitz(image_file, output_pdf)