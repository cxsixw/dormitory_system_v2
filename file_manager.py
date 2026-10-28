# ============================================================
# file_manager.py
# 민원 첨부 사진 저장 / 검사 / 삭제
#
# 사진 파일은 uploads/complaints/<민원번호>/ 폴더에 복사해서 저장하고,
# DB(ATTACHMENT 테이블)에는 파일 이름과 경로만 기록한다.
# ============================================================

import os
import shutil
import uuid


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "complaints")

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]
MAX_FILE_SIZE = 10 * 1024 * 1024   # 10MB
MAX_PHOTO_COUNT = 3


# ============================================================
# 사진 파일 검사
# 문제가 있으면 오류 메시지, 없으면 None
# ============================================================

def validate_image(file_path):

    file_name = os.path.basename(file_path)
    extension = os.path.splitext(file_name)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return f"{file_name}\njpg, jpeg, png 사진만 첨부할 수 있습니다."

    if not os.path.isfile(file_path):
        return f"{file_name}\n파일을 찾을 수 없습니다."

    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        return f"{file_name}\n10MB 이하의 사진만 첨부할 수 있습니다."

    return None


# ============================================================
# 사진 저장
# 원본을 민원번호 폴더에 새 이름으로 복사하고, DB에 기록할 정보를 돌려준다.
# ============================================================

def save_attachment(complaint_id, source_path):

    original_name = os.path.basename(source_path)
    extension = os.path.splitext(original_name)[1].lower()

    # 같은 이름의 사진이 덮어써지지 않도록 무작위 이름 사용
    stored_name = uuid.uuid4().hex + extension

    folder = os.path.join(UPLOAD_DIR, str(complaint_id))
    os.makedirs(folder, exist_ok=True)

    shutil.copyfile(source_path, os.path.join(folder, stored_name))

    return {
        "original_name": original_name,
        "stored_name": stored_name,
        # DB에는 프로그램 폴더 기준 상대 경로를 저장
        "file_path": f"uploads/complaints/{complaint_id}/{stored_name}",
        "file_size": os.path.getsize(source_path),
    }


# ============================================================
# DB에 저장된 경로 → 실제 파일 위치
# ============================================================

def get_absolute_path(file_path):

    return os.path.normpath(os.path.join(BASE_DIR, file_path))


# ============================================================
# 민원의 사진 폴더 삭제 (민원 저장에 실패했을 때 정리용)
# ============================================================

def delete_complaint_files(complaint_id):

    shutil.rmtree(
        os.path.join(UPLOAD_DIR, str(complaint_id)),
        ignore_errors=True
    )
