# ============================================================
# db.py
# MySQL 연결과 SQL 실행만 담당한다.
# 접속 정보(주소, 비밀번호 등)는 db_config.py 에서 읽는다.
# ============================================================

from contextlib import contextmanager


class DBError(Exception):
    """DB 연결 / 처리 중 문제가 생겼을 때 (화면에 그대로 보여줄 메시지를 담는다)"""


class DuplicateError(DBError):
    """UNIQUE / PRIMARY KEY 중복으로 저장하지 못했을 때"""


def _load_pymysql():

    try:
        import pymysql
    except ImportError:
        raise DBError(
            "pymysql 라이브러리가 설치되지 않았습니다.\n"
            "터미널에서  pip install pymysql  을 실행해주세요."
        )

    return pymysql


# ============================================================
# MySQL 연결
# ============================================================

def get_connection():

    pymysql = _load_pymysql()

    try:
        import db_config
    except ImportError:
        raise DBError(
            "db_config.py 파일이 없습니다.\n"
            "db_config_example.py 를 복사해서 db_config.py 를 만들어주세요."
        )

    try:
        return pymysql.connect(
            **db_config.DB_CONFIG,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5,
        )
    except pymysql.MySQLError:
        raise DBError(
            "DB 서버에 연결할 수 없습니다.\n"
            "① MySQL이 실행 중인지\n"
            "② db_config.py 의 비밀번호가 맞는지\n"
            "③ dormitory 데이터베이스를 만들었는지 확인해주세요."
        )


# ============================================================
# SQL 실행
# fetch : "none" → 영향받은 행 수 / "one" → 한 줄(dict) / "all" → 여러 줄(list)
# ============================================================

def execute_query(sql, params=(), fetch="none"):

    pymysql = _load_pymysql()

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute(sql, params)

            if fetch == "one":
                result = cursor.fetchone()
            elif fetch == "all":
                result = cursor.fetchall()
            else:
                result = cursor.rowcount

        conn.commit()

        return result

    except pymysql.err.IntegrityError:
        conn.rollback()
        raise DuplicateError("이미 존재하는 값입니다.")

    except pymysql.MySQLError as error:
        conn.rollback()
        raise DBError(f"DB 처리 중 오류가 발생했습니다.\n{error}")

    finally:
        conn.close()


# ============================================================
# 여러 SQL을 한 번에 처리 (트랜잭션)
# with 블록 안의 SQL이 모두 성공하면 저장(commit),
# 중간에 하나라도 실패하면 전부 취소(rollback)한다.
#
# 사용 예)
#   with transaction() as cursor:
#       cursor.execute("INSERT ...", (...))
#       new_id = cursor.lastrowid
# ============================================================

@contextmanager
def transaction():

    pymysql = _load_pymysql()

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            yield cursor

        conn.commit()

    except pymysql.err.IntegrityError:
        conn.rollback()
        raise DuplicateError("이미 존재하는 값이거나 연결된 데이터가 없습니다.")

    except pymysql.MySQLError as error:
        conn.rollback()
        raise DBError(f"DB 처리 중 오류가 발생했습니다.\n{error}")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
