# ============================================================
# complaint.py
# 민원 저장 / 조회 / 처리 상태 변경
#
# 사용 테이블 : COMPLAINT, COMPLAINT_TYPE, LOCATION, ATTACHMENT,
#              REPORT_HISTORY, STUDENT, ADMIN
# ============================================================

from db import execute_query, transaction, DBError
import file_manager


# 처리 상태 (순서대로 진행)
STATUS_LIST = ["접수", "확인", "처리 중", "완료"]

# 화면의 '발생 위치' 중 기숙사 방 → (구분)
ROOM_LOCATIONS = {
    "기숙사 방(여)": "여",
    "기숙사 방(남)": "남",
}


# ============================================================
# 민원 유형 번호 찾기 (없으면 새로 등록)
# ============================================================

def _get_or_create_type(cursor, category, type_name):

    cursor.execute(
        "SELECT type_id FROM COMPLAINT_TYPE "
        "WHERE category = %s AND type_name = %s",
        (category, type_name)
    )

    row = cursor.fetchone()

    if row is not None:
        return row["type_id"]

    cursor.execute(
        "INSERT INTO COMPLAINT_TYPE (category, type_name) VALUES (%s, %s)",
        (category, type_name)
    )

    return cursor.lastrowid


# ============================================================
# 위치 번호 찾기 (없으면 새로 등록)
# 기숙사 방 : 구분(여/남) + 층 + 호수
# 그 외     : 구분 '공용' + 장소 이름 (층/호수 없음)
# ============================================================

def _get_or_create_location(cursor, location_text, floor, room_no):

    if location_text in ROOM_LOCATIONS:

        dorm_section = ROOM_LOCATIONS[location_text]
        place_type = "기숙사 방"
        location_name = f"{dorm_section} {floor}층 {room_no}호"

    else:

        dorm_section = "공용"
        place_type = location_text
        floor = None
        room_no = None
        location_name = location_text

    # <=> : NULL 끼리도 같다고 비교하는 MySQL 연산자
    cursor.execute(
        "SELECT location_id FROM LOCATION "
        "WHERE dorm_section = %s AND floor <=> %s "
        "AND place_type = %s AND room_no <=> %s",
        (dorm_section, floor, place_type, room_no)
    )

    row = cursor.fetchone()

    if row is not None:
        return row["location_id"]

    cursor.execute(
        "INSERT INTO LOCATION "
        "(dorm_section, floor, place_type, room_no, location_name) "
        "VALUES (%s, %s, %s, %s, %s)",
        (dorm_section, floor, place_type, room_no, location_name)
    )

    return cursor.lastrowid


# ============================================================
# 민원 접수 (+ 사진 첨부)
# data : {category, problem_type, location, floor, room_no, content}
# 결과 : 새 민원 번호
# DB나 사진 저장에 실패하면 DBError 가 발생하고, 아무것도 저장되지 않는다.
# ============================================================

def create_complaint(student_id, data, image_paths):

    complaint_id = None

    try:
        with transaction() as cursor:

            type_id = _get_or_create_type(
                cursor,
                data["category"],
                data["problem_type"]
            )

            location_id = _get_or_create_location(
                cursor,
                data["location"],
                data.get("floor"),
                data.get("room_no")
            )

            cursor.execute(
                "INSERT INTO COMPLAINT "
                "(student_id, type_id, location_id, content) "
                "VALUES (%s, %s, %s, %s)",
                (student_id, type_id, location_id, data["content"])
            )

            complaint_id = cursor.lastrowid

            for path in image_paths:

                info = file_manager.save_attachment(complaint_id, path)

                cursor.execute(
                    "INSERT INTO ATTACHMENT "
                    "(complaint_id, original_name, stored_name, file_path, file_size) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (
                        complaint_id,
                        info["original_name"],
                        info["stored_name"],
                        info["file_path"],
                        info["file_size"],
                    )
                )

    except OSError as error:
        # 사진 복사 실패 → DB는 이미 취소됨, 복사된 사진도 정리
        if complaint_id is not None:
            file_manager.delete_complaint_files(complaint_id)
        raise DBError(f"사진을 저장하지 못했습니다.\n{error}")

    except DBError:
        if complaint_id is not None:
            file_manager.delete_complaint_files(complaint_id)
        raise

    return complaint_id


# ============================================================
# 내 신고 내역 (학생)
# ============================================================

def get_my_complaints(student_id):

    return execute_query(
        "SELECT c.complaint_id, c.status, c.created_at, "
        "       t.category, t.type_name, l.location_name "
        "FROM COMPLAINT c "
        "JOIN COMPLAINT_TYPE t ON c.type_id = t.type_id "
        "JOIN LOCATION l ON c.location_id = l.location_id "
        "WHERE c.student_id = %s "
        "ORDER BY c.created_at DESC, c.complaint_id DESC",
        (student_id,),
        fetch="all"
    )


# ============================================================
# 전체 신고 목록 (관리자) - status 를 주면 그 상태만
# ============================================================

def get_all_complaints(status=None):

    sql = (
        "SELECT c.complaint_id, c.status, c.created_at, c.student_id, "
        "       s.name AS student_name, t.category, t.type_name, l.location_name "
        "FROM COMPLAINT c "
        "JOIN STUDENT s ON c.student_id = s.student_id "
        "JOIN COMPLAINT_TYPE t ON c.type_id = t.type_id "
        "JOIN LOCATION l ON c.location_id = l.location_id "
    )

    params = ()

    if status is not None:
        sql += "WHERE c.status = %s "
        params = (status,)

    sql += "ORDER BY c.created_at DESC, c.complaint_id DESC"

    return execute_query(sql, params, fetch="all")


# ============================================================
# 신고 상세 (내용 + 사진 + 처리 이력)
# 결과 : dict (없는 민원이면 None)
# ============================================================

def get_complaint_detail(complaint_id):

    detail = execute_query(
        "SELECT c.complaint_id, c.student_id, s.name AS student_name, "
        "       c.content, c.status, c.created_at, c.updated_at, c.completed_at, "
        "       t.category, t.type_name, l.location_name "
        "FROM COMPLAINT c "
        "JOIN STUDENT s ON c.student_id = s.student_id "
        "JOIN COMPLAINT_TYPE t ON c.type_id = t.type_id "
        "JOIN LOCATION l ON c.location_id = l.location_id "
        "WHERE c.complaint_id = %s",
        (complaint_id,),
        fetch="one"
    )

    if detail is None:
        return None

    detail["attachments"] = execute_query(
        "SELECT attachment_id, original_name, file_path "
        "FROM ATTACHMENT WHERE complaint_id = %s "
        "ORDER BY attachment_id",
        (complaint_id,),
        fetch="all"
    )

    detail["history"] = execute_query(
        "SELECT h.prev_status, h.new_status, h.response_text, h.changed_at, "
        "       a.name AS admin_name "
        "FROM REPORT_HISTORY h "
        "JOIN ADMIN a ON h.admin_id = a.admin_id "
        "WHERE h.complaint_id = %s "
        "ORDER BY h.changed_at, h.history_id",
        (complaint_id,),
        fetch="all"
    )

    return detail


# ============================================================
# 처리 상태 변경 + 답변 등록 (관리자)
# 결과 : (성공 여부, 안내 메시지)
# ============================================================

def update_status(complaint_id, admin_id, new_status, response_text):

    if new_status not in STATUS_LIST:
        return False, "올바르지 않은 처리 상태입니다."

    response_text = response_text.strip() or None

    with transaction() as cursor:

        cursor.execute(
            "SELECT status FROM COMPLAINT WHERE complaint_id = %s FOR UPDATE",
            (complaint_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return False, "민원을 찾을 수 없습니다."

        prev_status = row["status"]

        if prev_status == new_status and response_text is None:
            return False, "변경된 상태나 답변이 없습니다."

        if new_status == "완료" and prev_status != "완료":
            completed_sql = "NOW()"          # 지금 완료됨
        elif new_status == "완료":
            completed_sql = "completed_at"   # 이미 완료 → 완료 시각 유지
        else:
            completed_sql = "NULL"           # 완료가 아니면 비움

        cursor.execute(
            "UPDATE COMPLAINT SET status = %s, updated_at = NOW(), "
            f"completed_at = {completed_sql} "
            "WHERE complaint_id = %s",
            (new_status, complaint_id)
        )

        cursor.execute(
            "INSERT INTO REPORT_HISTORY "
            "(complaint_id, admin_id, prev_status, new_status, response_text) "
            "VALUES (%s, %s, %s, %s, %s)",
            (complaint_id, admin_id, prev_status, new_status, response_text)
        )

    return True, "처리 내용이 저장되었습니다."


# ============================================================
# 날짜 표시용 (예: 2026-10-29 14:05)
# ============================================================

def format_datetime(value):

    if value is None:
        return "-"

    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M")

    return str(value)[:16]
