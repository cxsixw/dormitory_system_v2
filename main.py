# ============================================================
# main.py
# 프로그램 시작 파일 (VS Code에서 이 파일을 실행)
# ============================================================

import sys

from PySide6.QtWidgets import QApplication

import ui_login


def main():

    app = QApplication(
        sys.argv
    )

    login_window = ui_login.create_login_window()

    login_window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
