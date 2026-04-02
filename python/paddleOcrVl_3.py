# 좌표계는 맞는다먄, 문단이 길어지면 한 박스로 읽어들이는 문제


import os
import fitz  # PyMuPDF
from paddleocr import PaddleOCRVL
from PIL import Image

def create_searchable_pdf_with_fitz(image_path, output_pdf_path):
    print("⏳ 엔진 초기화 및 이미지 분석 중...")
    # 1. OCR 엔진 설정
    ocr = PaddleOCRVL(
        device="gpu", 
        use_layout_detection=True,
        use_doc_orientation_classify=False, 
        use_doc_unwarping=False,
        use_ocr_for_image_block=False,
        merge_layout_blocks=False,
    )
    
    # 2. 이미지 크기 확인 및 PDF 스케일링 계산
    img = Image.open(image_path)
    img_w, img_h = img.size
    
    # PDF 페이지 크기 제한 (450x650pt)
    max_h, max_w = 650.0, 450.0
    scaling_factor = min(max_w / img_w, max_h / img_h)
    
    pdf_w = img_w * scaling_factor
    pdf_h = img_h * scaling_factor

    # 3. PDF 문서 및 페이지 생성
    doc = fitz.open()
    page = doc.new_page(width=pdf_w, height=pdf_h) 
    
    # 배경 이미지 삽입 (페이지 크기에 맞춤)
    page.insert_image(page.rect, filename=image_path)
    
    # 폰트 설정 (Windows 기준 맑은 고딕)
    font_path = "C:/Windows/Fonts/malgun.ttf"
    page.insert_font(fontname="ko", fontfile=font_path)

    # 4. OCR 실행
    # use_doc_preprocessor=False로 모델의 임의 회전을 방지합니다.
    results = ocr.predict(image_path, format_block_content=False, use_doc_preprocessor=False) 
    
    # 한 줄 단위 결과 리스트 추출
    parsing_res = results[0]['parsing_res_list']
    print(f"🔎 총 {len(parsing_res)}개의 텍스트 라인을 삽입합니다.")
    print(results)

    # 5. 데이터 순회 및 텍스트 레이어 삽입
    for i, item in enumerate(parsing_res):
        # 객체(Object) 형태의 item에서 속성 추출
        bbox = getattr(item, 'bbox', None)      # [x1, y1, x2, y2] 원본 픽셀 좌표
        content = getattr(item, 'content', '').strip() # 인식된 글자
        
        # 유효한 데이터인 경우에만 진행
        if bbox and content:
            # [핵심] 원본 좌표를 PDF 좌표계(pt)로 변환
            pdf_x1 = float(bbox[0]) * scaling_factor
            pdf_y1 = float(bbox[1]) * scaling_factor
            pdf_x2 = float(bbox[2]) * scaling_factor
            pdf_y2 = float(bbox[3]) * scaling_factor
            
            # 변환된 박스의 높이 계산
            box_h = pdf_y2 - pdf_y1
            
            # 폰트 크기: 박스 높이의 90% 수준
            f_size = box_h * 0.9
            
            # y축(Baseline) 보정: 
            # PyMuPDF의 insert_text는 글자 바닥 기준입니다.
            # 박스 하단(pdf_y2)에서 높이의 약 15~20% 지점을 위로 올리면 
            # 이미지 글자 위치와 가장 잘 겹칩니다.
            insert_y = pdf_y2 - (box_h * 0.15) 

            try:
                page.insert_text(
                    (pdf_x1, insert_y), 
                    content, 
                    fontsize=f_size,
                    fontname="ko",
                    render_mode=0  # 0: 확인용(검정글씨 보임), 3: 투명(최종본용)
                )
            except Exception as e:
                print(f"❌ [라인 {i}] 삽입 실패: {e}")

    # 6. 결과 저장
    output_dir = os.path.dirname(output_pdf_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    doc.save(output_pdf_path)
    doc.close()
    print(f"\n🏁 PDF 생성 완료: {output_pdf_path}")

# --- 실행부 ---
if __name__ == "__main__":
    # 경로 설정 (사용자 환경에 맞게 수정)
    base_dir = r"C:\OCR_test\ocr_test1"
    image_file = os.path.join(base_dir, "00000006.jpg")
    output_pdf = os.path.join(base_dir, "output", "00000006_최종보정본.pdf")
    
    if os.path.exists(image_file):
        create_searchable_pdf_with_fitz(image_file, output_pdf)
    else:
        print(f"❌ 파일을 찾을 수 없습니다: {image_file}")