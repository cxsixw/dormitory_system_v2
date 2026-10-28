# ============================================================
# ui_login.py
# 로그인 화면 + 회원가입 화면
# ============================================================

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFrame,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from styles import APP_STYLE

import auth
import ui_student
from db import DBError


# ============================================================
# 로그인 화면
# ============================================================

def create_login_window():

    global window
    global id_input
    global password_input

    window = QWidget()

    window.setWindowTitle(
        "기숙사 시설 관리 시스템"
    )

    window.resize(520, 650)

    window.setStyleSheet(
        APP_STYLE
    )

    layout = QVBoxLayout()

    layout.setContentsMargins(
        65,
        55,
        65,
        45
    )

    layout.setSpacing(12)

    layout.addStretch()

    # 로그인 카드
    login_card = QFrame()
    login_card.setObjectName(
        "card"
    )

    card_layout = QVBoxLayout()

    card_layout.setContentsMargins(
        35,
        35,
        35,
        30
    )

    card_layout.setSpacing(12)

    # 건물 아이콘
    building = QLabel("🏢")

    building.setAlignment(
        Qt.AlignCenter
    )

    building.setFont(
        QFont("Arial", 42)
    )

    # 시스템 제목
    system_title = QLabel(
        "기숙사 시설 관리 시스템"
    )

    system_title.setObjectName(
        "title"
    )

    system_title.setAlignment(
        Qt.AlignCenter
    )

    # 부제목
    subtitle = QLabel(
        "학생 로그인"
    )

    subtitle.setObjectName(
        "subtitle"
    )

    subtitle.setAlignment(
        Qt.AlignCenter
    )

    card_layout.addWidget(building)
    card_layout.addWidget(system_title)
    card_layout.addWidget(subtitle)

    card_layout.addSpacing(15)

    # 학번
    id_label = QLabel("학번")
    id_label.setObjectName("label")

    id_input = QLineEdit()

    id_input.setPlaceholderText(
        "학번을 입력하세요"
    )

    id_input.setFixedHeight(44)

    # 학번에서 엔터 → 비밀번호 칸으로 이동
    id_input.returnPressed.connect(
        lambda: password_input.setFocus()
    )

    card_layout.addWidget(id_label)
    card_layout.addWidget(id_input)

    # 비밀번호
    password_label = QLabel("비밀번호")
    password_label.setObjectName("label")

    password_input = QLineEdit()

    password_input.setPlaceholderText(
        "비밀번호를 입력하세요"
    )

    password_input.setEchoMode(
        QLineEdit.Password
    )

    password_input.setFixedHeight(44)

    # 비밀번호에서 엔터 → 로그인
    password_input.returnPressed.connect(
        login
    )

    card_layout.addWidget(password_label)
    card_layout.addWidget(password_input)

    card_layout.addSpacing(5)

    # 로그인
    login_button = QPushButton(
        "로그인"
    )

    login_button.setObjectName(
        "blueButton"
    )

    login_button.setFixedHeight(46)

    login_button.clicked.connect(
        login
    )

    card_layout.addWidget(login_button)

    card_layout.addSpacing(2)

    # 회원가입 / 비밀번호 찾기
    bottom_layout = QHBoxLayout()

    signup_button = QPushButton(
        "회원가입"
    )

    signup_button.setObjectName(
        "subButton"
    )

    signup_button.clicked.connect(
        show_signup_window
    )

    find_button = QPushButton(
        "비밀번호 찾기"
    )

    find_button.setObjectName(
        "subButton"
    )

    bottom_layout.addStretch()

    bottom_layout.addWidget(
        signup_button
    )

    bottom_layout.addWidget(
        find_button
    )

    bottom_layout.addStretch()

    card_layout.addLayout(
        bottom_layout
    )

    login_card.setLayout(
        card_layout
    )

    layout.addWidget(
        login_card
    )

    layout.addStretch()

    # 하단 안내
    footer = QLabel(
        "Dormitory Facility Management System"
    )

    footer.setObjectName(
        "subtitle"
    )

    footer.setAlignment(
        Qt.AlignCenter
    )

    layout.addWidget(footer)

    window.setLayout(layout)

    return window


# ============================================================
# 로그인
# 가입된 학번 + 맞는 비밀번호일 때만 메인 화면으로 이동
# ============================================================

def login():

    student_id = id_input.text().strip()
    password = password_input.text()

    if student_id == "" or password == "":

        QMessageBox.warning(
            window,
            "로그인",
            "학번과 비밀번호를 입력해주세요."
        )

        return

    try:
        student = auth.login(student_id, password)
    except DBError as error:

        QMessageBox.critical(
            window,
            "DB 오류",
            str(error)
        )

        return

    # 없는 학번이거나 비밀번호가 틀린 경우
    if student is None:

        QMessageBox.warning(
            window,
            "로그인 실패",
            "학번 또는 비밀번호가 올바르지 않습니다."
        )

        password_input.clear()
        password_input.setFocus()

        return

    # 로그인 성공
    password_input.clear()
    window.hide()

    ui_student.show_main_window(student, back_to_login_after_logout)


# ============================================================
# 회원가입 화면
# ============================================================

def show_signup_window():

    window.hide()

    global signup_window
    global signup_inputs

    signup_window = QWidget()
    signup_window.setWindowTitle("회원가입")
    signup_window.resize(520, 720)
    signup_window.setStyleSheet(APP_STYLE)

    layout = QVBoxLayout()
    layout.setContentsMargins(65, 40, 65, 35)
    layout.setSpacing(12)

    layout.addStretch()

    # 회원가입 카드
    signup_card = QFrame()
    signup_card.setObjectName("card")

    card_layout = QVBoxLayout()
    card_layout.setContentsMargins(35, 30, 35, 28)
    card_layout.setSpacing(8)

    title = QLabel("회원가입")
    title.setObjectName("title")
    title.setAlignment(Qt.AlignCenter)

    subtitle = QLabel("학생 계정 정보를 입력해주세요.")
    subtitle.setObjectName("subtitle")
    subtitle.setAlignment(Qt.AlignCenter)

    card_layout.addWidget(title)
    card_layout.addWidget(subtitle)

    card_layout.addSpacing(10)

    # 입력 칸 : (저장 이름, 라벨, 안내 문구, 비밀번호 여부)
    fields = [
        ("student_id", "학번", "학번을 입력하세요", False),
        ("name", "이름", "이름을 입력하세요", False),
        ("email", "이메일", "example@email.com", False),
        ("password", "비밀번호", f"{auth.MIN_PASSWORD_LENGTH}자 이상 입력하세요", True),
        ("password_confirm", "비밀번호 확인", "비밀번호를 한 번 더 입력하세요", True),
    ]

    signup_inputs = {}

    for key, label_text, placeholder, is_password in fields:

        label = QLabel(label_text)
        label.setObjectName("label")

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setFixedHeight(42)

        if is_password:
            line_edit.setEchoMode(QLineEdit.Password)

        card_layout.addWidget(label)
        card_layout.addWidget(line_edit)

        signup_inputs[key] = line_edit

    # 엔터 → 다음 칸으로, 마지막 칸에서 엔터 → 가입
    input_list = list(signup_inputs.values())

    for current, next_input in zip(input_list, input_list[1:]):
        current.returnPressed.connect(next_input.setFocus)

    input_list[-1].returnPressed.connect(signup)

    card_layout.addSpacing(8)

    # 가입하기
    signup_button = QPushButton("가입하기")
    signup_button.setObjectName("blueButton")
    signup_button.setFixedHeight(46)
    signup_button.clicked.connect(signup)

    card_layout.addWidget(signup_button)

    signup_card.setLayout(card_layout)

    layout.addWidget(signup_card)

    # 로그인으로
    back_button = QPushButton("← 로그인 화면으로")
    back_button.setObjectName("backButton")
    back_button.clicked.connect(back_to_login_from_signup)

    layout.addWidget(
        back_button,
        alignment=Qt.AlignCenter
    )

    layout.addStretch()

    signup_window.setLayout(layout)

    signup_window.show()

    signup_inputs["student_id"].setFocus()


# ============================================================
# 가입하기 버튼 → 계정 저장
# ============================================================

def signup():

    info = {
        key: line_edit.text().strip()
        for key, line_edit in signup_inputs.items()
    }

    # 비밀번호는 앞뒤 공백도 그대로 사용
    info["password"] = signup_inputs["password"].text()
    info["password_confirm"] = signup_inputs["password_confirm"].text()

    try:
        success, message = auth.register_student(info)
    except DBError as error:

        QMessageBox.critical(
            signup_window,
            "DB 오류",
            str(error)
        )

        return

    if not success:

        QMessageBox.warning(
            signup_window,
            "회원가입",
            message
        )

        return

    QMessageBox.information(
        signup_window,
        "회원가입",
        message
    )

    # 로그인 화면으로 돌아가서 학번 미리 채워주기
    back_to_login_from_signup()

    id_input.setText(info["student_id"])
    password_input.setFocus()


# ============================================================
# 회원가입 → 로그인
# ============================================================

def back_to_login_from_signup():

    signup_window.close()

    password_input.clear()
    window.show()


# ============================================================
# 로그아웃 → 로그인 화면 (학생 화면에서 호출)
# ============================================================

def back_to_login_after_logout():

    id_input.clear()
    password_input.clear()

    window.show()

    id_input.setFocus()