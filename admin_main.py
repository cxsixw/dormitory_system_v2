# ============================================================
# admin_main.py
# 관리자 프로그램 시작 파일 (관리자 PC에서 이 파일을 실행)
# ============================================================

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

import ui_admin


def main():

    app = QApplication(
        sys.argv
    )

    login_window = ui_admin.create_admin_login_window()

    login_window.show()

    # 창이 뜬 직후, 관리자 계정이 없으면 최초 관리자 등록 창을 띄움
    QTimer.singleShot(0, ui_admin.check_first_admin)

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
