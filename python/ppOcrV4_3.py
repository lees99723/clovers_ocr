#  <이미지 파일 하나 받아서 ocr기능 들어간 pdf 생성>
# PP-OCRv4 (2.8.1 안정 버전) 사용 및 스마트 크기 맞춤 적용
# 이미지 크기 조정

# <언어팩 문제>
# 사용자정의 언어 txt 파일 로드(한글,한자,영어 포함했으나 모델의 인식률이 낮음)
# 1. ocr클래스를 로드할때 처음 불러온 언어모델이 먼저 문자판단 -> 인덱스를 던져
# 2. 사전에서는 해당 문자의 인덱스를 통해 문자를 불러오기 때문에 결국 똑같음
# 만약 ocr클래스 객체를 언어마다 만든다고 해도 '노신사老仲主'같은 경우가 한 텍스트로 잡혀서 인식하면 결국 한 언어만 선택해야함

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
# 엔진 오류 방지
os.environ['FLAGS_use_onednn'] = '0'
os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'

from paddleocr import PaddleOCR
from PIL import Image

def create_searchable_pdf_with_fitz(image_path, output_pdf_path):
    # 1. OCR 초기화 (기존 동일)
    print("⏳ 엔진 초기화 중...")
    
    dict_path = "C:/eGovFrameDev-4.3.1-64bit/workspace-egov/ocr/python/dict/ppocrv4_doc_dict.txt"
    
    ocr = PaddleOCR(
        lang='korean', # 반드시 내부적으로 특정 lang에 매칭되는 파일을 로드해야만 작동
        rec_char_dict_path=dict_path, # 전체 글자목록이 담겼지만 결국 내부적으로 인식한 언어 한정해서 읽어올수 일뿐
        det_db_unclip_ratio=1.6,
        ocr_version='PP-OCRv4',
        use_angle_cls=True,
        show_log=False,
    )
    
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
    

    
    # 3. OCR 수행 (원본 이미지로 수행)
    print(f"🚀 분석 시작: {image_path}")
    results = ocr.ocr(image_path, cls=True)
    
    if not results or results[0] is None:
        print("❌ 인식된 데이터가 없습니다.")
        doc.close()
        return

    font_path = "C:/Windows/Fonts/malgun.ttf"
    data_list = results[0]
    print(f"📝 총 {len(data_list)}개의 문장을 PDF에 심는 중...")
    print(results)
    
    for line in data_list:
        try:
            box = line[0]          # 좌표 (4개의 점, 원본 이미지 기준 pixel 단위)
            text = line[1][0]      # 인식된 글자
            #print(f"{text:<25}")
            if not text.strip(): continue
                
            # [🔥 핵심 수정 포인트] 원본 거대 좌표에 scaling_factor를 곱해서 
            # 작아진 PDF 종이 좌표(pt 단위)로 재계산합니다.
            x_coords = [p[0] * scaling_factor for p in box]
            y_coords = [p[1] * scaling_factor for p in box]
            
            # 작아진 좌표로 Rect 생성
            rect = fitz.Rect(min(x_coords), min(y_coords), max(x_coords), max(y_coords))
            
            # 텍스트 삽입 (render_mode=3으로 투명하게)
            page.insert_text(
                (rect.x0, rect.y1 - (rect.height * 0.1)), # 위치 미세 보정
                text, 
                # fontsize도 작아진 rect 높이에 맞춥니다.
                fontsize=rect.height * 0.85, 
                fontfile=font_path,
                fontname="ko",     
                render_mode=3      
            )
            
        except Exception as e:
            # print(f"⚠️ 개별 문장 오류 발생: {e}")
            continue

    # 6. 저장 및 출력 디렉토리 확인
    output_dir = os.path.dirname(output_pdf_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    doc.save(output_pdf_path)
    doc.close()
    print(f"\n🏁 OCR PDF 생성완료: {output_pdf_path}")


if __name__ == "__main__":
    base_dir = r"C:\OCR_test\ocr_test1"
    image_file = os.path.join(base_dir, "00000222.jpg")
    output_pdf = os.path.join(base_dir, "output", "00000222.pdf")
    
    if os.path.exists(image_file):
        create_searchable_pdf_with_fitz(image_file, output_pdf)