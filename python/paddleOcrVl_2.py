import os
import fitz  # PyMuPDF
# 엔진 오류 방지
os.environ['FLAGS_use_onednn'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCRVL
from PIL import Image

def create_searchable_pdf_with_fitz(image_path, output_pdf_path):
    # 1. OCR 초기화 (기존 동일)
    print("⏳ 엔진 초기화 중...")
    ocr = PaddleOCRVL(device="gpu", use_layout_detection=False)
    
    # 2. 이미지 정보 및 스마트 배율 계산
    img = Image.open(image_path)
    img_w, img_h = img.size # 예: 1476, 2409
    
    max_h = 650.0 # 세로 높이 제한
    max_w = 450.0 # 가로 너비 제한

    # 가로/세로 중 비율을 더 많이 줄여야 하는 쪽을 선택
    scaling_factor = min(max_w / img_w, max_h / img_h)
    
    # 최종 PDF 종이 크기 결정
    pdf_w = img_w * scaling_factor
    pdf_h = img_h * scaling_factor

    # PyMuPDF로 PDF 생성 시작
    doc = fitz.open()
    # 계산된 크기로 페이지 생성
    page = doc.new_page(width=pdf_w, height=pdf_h) 
    # 이미지를 작아진 페이지 크기에 맞게 삽입
    page.insert_image(page.rect, filename=image_path)
    

    
    # 3. OCR 수행 (결과값은 dict 형태임)
    results = ocr.predict(image_path, format_block_content=True) 
    font_path = "C:/Windows/Fonts/malgun.ttf"
    # PaddleOCRVL의 결과는 보통 리스트 안에 딕셔너리가 들어있는 구조입니다.
    # 위에서 보여주신 구조에 따라 parsing_res_list를 타겟팅합니다.
    data_list = results[0].get('parsing_res_list', [])

    print(data_list)

    for item in data_list:
        try:
            
            box = item.bbox      # [xmin, ymin, xmax, ymax] 형태
            text = item.content  # 인식된 글자
            print(box)
            print(text)
            
            #if not text.strip(): continue

            x1, y1, x2, y2 = [coord * scaling_factor for coord in box]
            
            # 2. PyMuPDF Rect 생성
            rect = fitz.Rect(x1, y1, x2, y2)

            font_size = (y2 - y1) * 0.85
            if font_size <= 0: font_size = 10 

            page.insert_text(
                (rect.x0, rect.y1 - (rect.height * 0.1)), 
                text,
                fontsize=font_size,
                fontfile=font_path,
                fontname="ko",
                render_mode=3 # 투명(검색만 가능)
            )
            
        except Exception as e:
            print(f"⚠️ 개별 문장 오류 발생: {e}")
            continue
    
    # data_list = results[0]
    # print(f"📝 총 {len(data_list)}개의 문장을 PDF에 심는 중...")
    
    # for line in data_list:
    #     try:
    #         box = line[0]          # 좌표 (4개의 점, 원본 이미지 기준 pixel 단위)
    #         text = line[1][0]      # 인식된 글자
    #         print(f"{text:<25}")
    #         if not text.strip(): continue
                
    #         # [🔥 핵심 수정 포인트] 원본 거대 좌표에 scaling_factor를 곱해서 
    #         # 작아진 PDF 종이 좌표(pt 단위)로 재계산합니다.
    #         x_coords = [p[0] * scaling_factor for p in box]
    #         y_coords = [p[1] * scaling_factor for p in box]
            
    #         # 작아진 좌표로 Rect 생성
    #         rect = fitz.Rect(min(x_coords), min(y_coords), max(x_coords), max(y_coords))
            
    #         # 텍스트 삽입 (render_mode=3으로 투명하게)
    #         page.insert_text(
    #             (rect.x0, rect.y1 - (rect.height * 0.1)), # 위치 미세 보정
    #             text, 
    #             # fontsize도 작아진 rect 높이에 맞춥니다.
    #             fontsize=rect.height * 0.85, 
    #             fontfile=font_path,
    #             fontname="ko",     
    #             render_mode=3      
    #         )
            
    #     except Exception as e:
    #         # print(f"⚠️ 개별 문장 오류 발생: {e}")
    #         continue

    # 6. 저장 및 출력 디렉토리 확인
    output_dir = os.path.dirname(output_pdf_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    doc.save(output_pdf_path)
    doc.close()
    print(f"\n🏁 OCR PDF 생성완료: {output_pdf_path}")


if __name__ == "__main__":
    base_dir = r"C:\OCR_test\ocr_test1"
    image_file = os.path.join(base_dir, "00000006.jpg")
    output_pdf = os.path.join(base_dir, "output", "1.pdf")
    
    if os.path.exists(image_file):
        create_searchable_pdf_with_fitz(image_file, output_pdf)