# ============================================================
# auth.py
# 학생 계정 관리 : 회원가입 저장 / 로그인 확인 / 내 정보 조회
#
# 계정은 MySQL 의 STUDENT 테이블에 저장한다. (db.py 사용)
# ============================================================

import hashlib
import hmac
import re
import secrets

from db import execute_query, DuplicateError, DBError  # DBError 는 화면에서도 사용


# 비밀번호 최소 길이
MIN_PASSWORD_LENGTH = 8


# ============================================================
# 비밀번호 암호화
# 비밀번호를 그대로 저장하지 않고 salt + 해시값으로 저장한다.
# (salt 32글자, 해시 64글자 → STUDENT 테이블의 CHAR(32), CHAR(64))
# ============================================================

def hash_password(password, salt=None):

    if salt is None:
        salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        100_000
    ).hex()

    return salt, hashed


# ============================================================
# 학번 중복 확인
# ============================================================

def check_duplicate_id(student_id):

    row = execute_query(
        "SELECT student_id FROM STUDENT WHERE student_id = %s",
        (student_id,),
        fetch="one"
    )

    return row is not None


# ============================================================
# 회원가입 입력값 검사
# 문제가 있으면 오류 메시지, 없으면 None을 돌려준다.
# ============================================================

def validate_signup(info):

    if (
        info["student_id"] == ""
        or info["name"] == ""
        or info["email"] == ""
        or info["password"] == ""
        or info["password_confirm"] == ""
    ):
        return "모든 항목을 입력해주세요."

    if not info["student_id"].isdigit():
        return "학번은 숫자만 입력해주세요."

    if len(info["student_id"]) > 20:
        return "학번이 너무 깁니다."

    if len(info["name"]) > 50:
        return "이름이 너무 깁니다."

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", info["email"]):
        return "이메일 형식이 올바르지 않습니다."

    if len(info["email"]) > 100:
        return "이메일이 너무 깁니다."

    if len(info["password"]) < MIN_PASSWORD_LENGTH:
        return f"비밀번호는 {MIN_PASSWORD_LENGTH}자 이상 입력해주세요."

    if info["password"] != info["password_confirm"]:
        return "비밀번호가 일치하지 않습니다."

    return None


# ============================================================
# 회원가입
# 결과 : (성공 여부, 안내 메시지)
# DB에 연결하지 못하면 DBError 가 발생한다.
# ============================================================

def register_student(info):

    error = validate_signup(info)

    if error is not None:
        return False, error

    if check_duplicate_id(info["student_id"]):
        return False, "이미 가입된 학번입니다."

    salt, hashed = hash_password(info["password"])

    try:
        execute_query(
            "INSERT INTO STUDENT (student_id, name, email, password_hash, salt) "
            "VALUES (%s, %s, %s, %s, %s)",
            (
                info["student_id"],
                info["name"],
                info["email"],
                hashed,
                salt,
            )
        )
    except DuplicateError:
        # 학번은 위에서 확인했으므로 이메일(UNIQUE) 중복
        return False, "이미 가입된 이메일입니다."

    return True, "회원가입이 완료되었습니다.\n가입한 학번으로 로그인해주세요."


# ============================================================
# 로그인 확인
# 성공 : 학생 정보 딕셔너리 / 실패 : None
# DB에 연결하지 못하면 DBError 가 발생한다.
# ============================================================

def login(student_id, password):

    user = execute_query(
        "SELECT student_id, name, email, password_hash, salt "
        "FROM STUDENT WHERE student_id = %s",
        (student_id,),
        fetch="one"
    )

    # 없는 학번
    if user is None:
        return None

    _, hashed = hash_password(password, user["salt"])

    # 비밀번호 틀림
    if not hmac.compare_digest(hashed, user["password_hash"]):
        return None

    return {
        "student_id": user["student_id"],
        "name": user["name"],
        "email": user["email"],
    }


# ============================================================
# 내 정보 조회 (비밀번호 정보는 빼고 돌려준다)
# ============================================================

def get_my_info(student_id):

    user = execute_query(
        "SELECT student_id, name, email FROM STUDENT WHERE student_id = %s",
        (student_id,),
        fetch="one"
    )

    return user


# ============================================================
# 비밀번호 변경 (학생)
# 결과 : (성공 여부, 안내 메시지)
# ============================================================

def change_password(student_id, current_password, new_password, new_password_confirm):

    if current_password == "" or new_password == "" or new_password_confirm == "":
        return False, "모든 항목을 입력해주세요."

    if login(student_id, current_password) is None:
        return False, "현재 비밀번호가 올바르지 않습니다."

    if len(new_password) < MIN_PASSWORD_LENGTH:
        return False, f"새 비밀번호는 {MIN_PASSWORD_LENGTH}자 이상 입력해주세요."

    if new_password != new_password_confirm:
        return False, "새 비밀번호가 일치하지 않습니다."

    if new_password == current_password:
        return False, "현재 비밀번호와 다른 비밀번호를 입력해주세요."

    salt, hashed = hash_password(new_password)

    execute_query(
        "UPDATE STUDENT SET password_hash = %s, salt = %s WHERE student_id = %s",
        (hashed, salt, student_id)
    )

    return True, "비밀번호가 변경되었습니다."


# ============================================================
# 관리자 계정이 하나라도 있는지 (최초 관리자 등록 여부 확인)
# ============================================================

def admin_exists():

    row = execute_query(
        "SELECT COUNT(*) AS cnt FROM ADMIN",
        fetch="one"
    )

    return row["cnt"] > 0


# ============================================================
# 관리자 등록
# info : {admin_id, name, password, password_confirm}
# 최초 관리자는 '최고 관리자' 권한으로 등록한다.
# ============================================================

def register_admin(info):

    if (
        info["admin_id"] == ""
        or info["name"] == ""
        or info["password"] == ""
        or info["password_confirm"] == ""
    ):
        return False, "모든 항목을 입력해주세요."

    if len(info["admin_id"]) > 20:
        return False, "아이디는 20자 이하로 입력해주세요."

    if len(info["password"]) < MIN_PASSWORD_LENGTH:
        return False, f"비밀번호는 {MIN_PASSWORD_LENGTH}자 이상 입력해주세요."

    if info["password"] != info["password_confirm"]:
        return False, "비밀번호가 일치하지 않습니다."

    role = "일반" if admin_exists() else "최고 관리자"

    salt, hashed = hash_password(info["password"])

    try:
        execute_query(
            "INSERT INTO ADMIN (admin_id, name, role, password_hash, salt) "
            "VALUES (%s, %s, %s, %s, %s)",
            (info["admin_id"], info["name"], role, hashed, salt)
        )
    except DuplicateError:
        return False, "이미 사용 중인 아이디입니다."

    return True, "관리자 계정이 등록되었습니다.\n등록한 아이디로 로그인해주세요."


# ============================================================
# 관리자 로그인
# 성공 : 관리자 정보 딕셔너리 / 실패 : None
# ============================================================

def admin_login(admin_id, password):

    admin = execute_query(
        "SELECT admin_id, name, role, is_active, password_hash, salt "
        "FROM ADMIN WHERE admin_id = %s",
        (admin_id,),
        fetch="one"
    )

    if admin is None or not admin["is_active"]:
        return None

    _, hashed = hash_password(password, admin["salt"])

    if not hmac.compare_digest(hashed, admin["password_hash"]):
        return None

    return {
        "admin_id": admin["admin_id"],
        "name": admin["name"],
        "role": admin["role"],
    }
