#  <이미지 파일 하나 받아서 ocr기능 들어간 pdf 생성>
# PP-OCRv4 (2.8.1 안정 버전) 사용 및 스마트 크기 맞춤 적용
# 이미지 크기 조정
# 사용자정의 언어 txt 파일 로드

#
# 1. 필수 설치 라이브러리 :
#    pip install paddlepaddle           OCR 구동 엔진 (CPU용)
#    pip install paddleocr              실제 글자를 읽어주는 함수포함
#    pip install opencv-python          이미지를 숫자 배열로 읽어서 OCR에 전달
#    pip install pillow                 이미지 크기(가로/세로) 확인
#    pip install pymupdf                PDF 생성 및 텍스트 레이어 삽입 (fitz)

# 꼬였을때
# 1. 꼬여있는 현재 버전들 싹 지우기
# pip uninstall paddlepaddle paddleocr paddlex -y
# 2. 검증된 안정 버전(2.8.1)으로 강제 설치
#pip install paddlepaddle==2.6.1 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
#pip install paddleocr==2.8.1
# 3. 기타 필요한 라이브러리 확인
#pip install pymupdf pillow opencv-python
   
# 2. 주의:
#    - os.environ 설정: Windows 환경에서의 엔진 충돌(oneDNN와의 충돌)방지 위해 가속기능 끄기 -> os.environ['FLAGS_use_onednn'] = '0'
#    - ocr.ocr은 결과를 리스트로 반환(이거쓰려면 paddleocr==2.8.1 버전 ), ocr.predict는 결과를 딕셔너리로 반환(결과값을 내부적으로 후처리하면서 좌표값 살짝 밀림)

import os
import fitz  # PyMuPDF
import cv2   # 이미지 확대를 위해 필요
import numpy as np
from paddleocr import PaddleOCR
from PIL import Image

# 엔진 오류 방지
os.environ['FLAGS_use_onednn'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

def create_searchable_pdf_with_fitz(image_path, output_pdf_path):
    print("⏳ 엔진 초기화 중...")
    
    # [설정] 인식률 향상을 위한 확대 배율 (2.0배 확대)
    upscale_factor = 2.0 
    
    ocr = PaddleOCR(
        lang='korean',
        ocr_version='PP-OCRv4',
        use_angle_cls=True,
        show_log=False,
        # 이미지가 커지므로 디텍션 제한도 함께 늘려줍니다.
        det_limit_side_len=4000 
    )
    
    # 1. 이미지 로드 및 PDF 기본 크기 계산
    img_pil = Image.open(image_path)
    img_w, img_h = img_pil.size
    
    max_h, max_w = 650.0, 450.0
    scaling_factor = min(max_w / img_w, max_h / img_h)
    pdf_w, pdf_h = img_w * scaling_factor, img_h * scaling_factor

    doc = fitz.open()
    page = doc.new_page(width=pdf_w, height=pdf_h) 
    page.insert_image(page.rect, filename=image_path)
    
    # 2. [핵심] OCR용 이미지 확대 (OpenCV 사용)
    # 한글 경로 문제를 방지하기 위해 numpy로 읽습니다.
    img_array = np.fromfile(image_path, np.uint8)
    img_cv = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    print(f"🔍 인식 정밀도 향상을 위해 이미지를 {upscale_factor}배 확대 중...")
    img_upscaled = cv2.resize(img_cv, None, fx=upscale_factor, fy=upscale_factor, interpolation=cv2.INTER_CUBIC)
    
    # 3. 확대된 이미지로 OCR 수행
    print(f"🚀 분석 시작 (확대 인식 모드): {image_path}")
    results = ocr.ocr(img_upscaled, cls=True)
    
    if not results or results[0] is None:
        print("❌ 인식된 데이터가 없습니다.")
        doc.close()
        return

    font_path = "C:/Windows/Fonts/malgun.ttf"
    data_list = results[0]
    print(f"📝 총 {len(data_list)}개의 문장을 PDF에 심는 중...")
    
    for line in data_list:
        try:
            # 확대된 이미지 기준의 뻥튀기된 좌표
            upscaled_box = line[0] 
            text = line[1][0]
            
            if not text.strip(): continue
            
            # [🔥 좌표 역계산 핵심]
            # 1. upscaled_box 좌표를 다시 원본 크기로 복구 (upscale_factor로 나눔)
            # 2. 원본 크기 좌표에 최종 PDF scaling_factor를 곱함
            x_coords = [(p[0] / upscale_factor) * scaling_factor for p in upscaled_box]
            y_coords = [(p[1] / upscale_factor) * scaling_factor for p in upscaled_box]
            
            # 복구된 좌표로 Rect 생성
            rect = fitz.Rect(min(x_coords), min(y_coords), max(x_coords), max(y_coords))
            
            # 텍스트 삽입 (위치 및 폰트 크기는 원래 박스 크기에 맞춰짐)
            # 괄호 에러 방지를 위해 위치를 튜플로 명시
            text_pos = (rect.x0, rect.y1 - (rect.height * 0.1))
            
            page.insert_text(
                text_pos,
                text, 
                fontsize=rect.height * 0.85, # 박스 높이에 맞춘 폰트 크기
                fontfile=font_path,
                fontname="ko",
                render_mode=3 
            )
            
        except Exception as e:
            continue

    # 4. 저장
    output_dir = os.path.dirname(output_pdf_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    doc.save(output_pdf_path)
    doc.close()
    print(f"\n🏁 확대 인식 PDF 생성완료: {output_pdf_path}")


if __name__ == "__main__":
    base_dir = r"C:\OCR_test\ocr_test1"
    image_file = os.path.join(base_dir, "00000006.jpg")
    output_pdf = os.path.join(base_dir, "output", "00000006.pdf")
    
    if os.path.exists(image_file):
        create_searchable_pdf_with_fitz(image_file, output_pdf)