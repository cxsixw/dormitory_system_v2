# ============================================================
# reset_admin_password.py
# 관리자 비밀번호를 잊어버렸을 때 새 비밀번호로 바꾸는 도구
# VS Code에서 ▶ 로 실행 → 아래 터미널에 아이디와 새 비밀번호 입력
# ============================================================

import auth
from db import execute_query, DBError


def main():

    try:
        admins = execute_query(
            "SELECT admin_id, name, role FROM ADMIN",
            fetch="all"
        )
    except DBError as error:
        print(error)
        return

    if len(admins) == 0:
        print("등록된 관리자가 없습니다. admin_main.py 를 실행해서 등록하세요.")
        return

    print("등록된 관리자 목록")
    for admin in admins:
        print(f" - 아이디: {admin['admin_id']}  ({admin['name']}, {admin['role']})")
    print()

    admin_id = input("비밀번호를 바꿀 관리자 아이디: ").strip()
    new_password = input(f"새 비밀번호 ({auth.MIN_PASSWORD_LENGTH}자 이상): ")

    if len(new_password) < auth.MIN_PASSWORD_LENGTH:
        print(f"비밀번호는 {auth.MIN_PASSWORD_LENGTH}자 이상이어야 합니다.")
        return

    salt, hashed = auth.hash_password(new_password)

    count = execute_query(
        "UPDATE ADMIN SET password_hash = %s, salt = %s WHERE admin_id = %s",
        (hashed, salt, admin_id)
    )

    if count == 1:
        print("비밀번호가 변경되었습니다. 관리자 프로그램에서 새 비밀번호로 로그인하세요.")
    else:
        print("해당 아이디의 관리자가 없습니다.")


if __name__ == "__main__":
    main()
