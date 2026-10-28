# ============================================================
# ui_admin.py
# 관리자 프로그램 화면
#   - 최초 관리자 등록 / 관리자 로그인
#   - 전체 민원 목록 (처리 상태로 거르기)
#   - 민원 상세 확인, 처리 상태 변경, 답변 등록
# ============================================================

from PySide6.QtWidgets import (
    QWidget,
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QFrame,
    QComboBox,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QBrush

from styles import APP_STYLE

import auth
import complaint
import ui_detail
from db import DBError


# 목록 위 '처리 상태' 선택 항목
STATUS_FILTERS = ["전체"] + complaint.STATUS_LIST

# 목록 표의 열 이름
TABLE_HEADERS = ["번호", "신고 일시", "학번", "이름", "민원 유형", "위치", "처리 상태"]

# 로그인한 관리자 정보 (admin_login 에서 채워짐)
current_admin = None


# ============================================================
# 관리자 로그인 화면
# ============================================================

def create_admin_login_window():

    global login_window
    global admin_id_input
    global admin_password_input

    login_window = QWidget()
    login_window.setWindowTitle("기숙사 시설 관리 시스템 - 관리자")
    login_window.resize(520, 650)
    login_window.setStyleSheet(APP_STYLE)

    layout = QVBoxLayout()
    layout.setContentsMargins(65, 55, 65, 45)
    layout.setSpacing(12)

    layout.addStretch()

    login_card = QFrame()
    login_card.setObjectName("card")

    card_layout = QVBoxLayout()
    card_layout.setContentsMargins(35, 35, 35, 30)
    card_layout.setSpacing(12)

    icon = QLabel("🛠️")
    icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon.setFont(QFont("Arial", 42))

    system_title = QLabel("기숙사 시설 관리 시스템")
    system_title.setObjectName("title")
    system_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    subtitle = QLabel("관리자 로그인")
    subtitle.setObjectName("subtitle")
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

    card_layout.addWidget(icon)
    card_layout.addWidget(system_title)
    card_layout.addWidget(subtitle)

    card_layout.addSpacing(15)

    # 아이디
    id_label = QLabel("관리자 아이디")
    id_label.setObjectName("label")

    admin_id_input = QLineEdit()
    admin_id_input.setPlaceholderText("아이디를 입력하세요")
    admin_id_input.setFixedHeight(44)

    # 비밀번호
    password_label = QLabel("비밀번호")
    password_label.setObjectName("label")

    admin_password_input = QLineEdit()
    admin_password_input.setPlaceholderText("비밀번호를 입력하세요")
    admin_password_input.setEchoMode(QLineEdit.EchoMode.Password)
    admin_password_input.setFixedHeight(44)

    # 엔터 : 아이디 → 비밀번호 칸, 비밀번호 → 로그인
    admin_id_input.returnPressed.connect(admin_password_input.setFocus)
    admin_password_input.returnPressed.connect(admin_login)

    card_layout.addWidget(id_label)
    card_layout.addWidget(admin_id_input)
    card_layout.addWidget(password_label)
    card_layout.addWidget(admin_password_input)

    card_layout.addSpacing(5)

    login_button = QPushButton("로그인")
    login_button.setObjectName("blueButton")
    login_button.setFixedHeight(46)
    login_button.clicked.connect(admin_login)

    card_layout.addWidget(login_button)

    login_card.setLayout(card_layout)

    layout.addWidget(login_card)

    layout.addStretch()

    footer = QLabel("Dormitory Facility Management System · Admin")
    footer.setObjectName("subtitle")
    footer.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(footer)

    login_window.setLayout(layout)

    return login_window


# ============================================================
# 프로그램 시작 직후 : 관리자 계정이 없으면 최초 관리자 등록
# ============================================================

def check_first_admin():

    try:
        exists = auth.admin_exists()
    except DBError as error:

        QMessageBox.critical(
            login_window,
            "DB 오류",
            str(error)
        )

        return

    if not exists:

        QMessageBox.information(
            login_window,
            "관리자 등록",
            "등록된 관리자 계정이 없습니다.\n"
            "최초 관리자 계정을 먼저 등록해주세요."
        )

        show_admin_register_dialog()


# ============================================================
# 관리자 등록 창
# ============================================================

def show_admin_register_dialog():

    dialog = QDialog(login_window)
    dialog.setWindowTitle("관리자 등록")
    dialog.resize(420, 520)
    dialog.setStyleSheet(APP_STYLE)

    layout = QVBoxLayout()
    layout.setContentsMargins(35, 30, 35, 25)
    layout.setSpacing(8)

    title = QLabel("관리자 등록")
    title.setObjectName("title")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)

    subtitle = QLabel("최초 관리자는 '최고 관리자' 권한으로 등록됩니다.")
    subtitle.setObjectName("subtitle")
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(title)
    layout.addWidget(subtitle)

    layout.addSpacing(10)

    # (저장 이름, 라벨, 비밀번호 여부)
    fields = [
        ("admin_id", "관리자 아이디", False),
        ("name", "이름", False),
        ("password", f"비밀번호 ({auth.MIN_PASSWORD_LENGTH}자 이상)", True),
        ("password_confirm", "비밀번호 확인", True),
    ]

    inputs = {}

    for key, label_text, is_password in fields:

        label = QLabel(label_text)
        label.setObjectName("label")

        line_edit = QLineEdit()
        line_edit.setFixedHeight(42)

        if is_password:
            line_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(label)
        layout.addWidget(line_edit)

        inputs[key] = line_edit

    def register():

        info = {
            "admin_id": inputs["admin_id"].text().strip(),
            "name": inputs["name"].text().strip(),
            "password": inputs["password"].text(),
            "password_confirm": inputs["password_confirm"].text(),
        }

        try:
            success, message = auth.register_admin(info)
        except DBError as error:

            QMessageBox.critical(
                dialog,
                "관리자 등록",
                str(error)
            )

            return

        if not success:

            QMessageBox.warning(
                dialog,
                "관리자 등록",
                message
            )

            return

        QMessageBox.information(
            dialog,
            "관리자 등록",
            message
        )

        dialog.accept()

        # 로그인 화면에 아이디 미리 채우기
        admin_id_input.setText(info["admin_id"])
        admin_password_input.setFocus()

    # 엔터 → 다음 칸, 마지막 칸에서 엔터 → 등록
    input_list = list(inputs.values())

    for current, next_input in zip(input_list, input_list[1:]):
        current.returnPressed.connect(next_input.setFocus)

    input_list[-1].returnPressed.connect(register)

    layout.addSpacing(10)

    register_button = QPushButton("등록하기")
    register_button.setObjectName("blueButton")
    register_button.setFixedHeight(46)
    register_button.clicked.connect(register)

    cancel_button = QPushButton("취소")
    cancel_button.setObjectName("backButton")
    cancel_button.clicked.connect(dialog.reject)

    layout.addWidget(register_button)
    layout.addWidget(cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)

    dialog.setLayout(layout)

    input_list[0].setFocus()

    dialog.exec()


# ============================================================
# 관리자 로그인
# ============================================================

def admin_login():

    global current_admin

    admin_id = admin_id_input.text().strip()
    password = admin_password_input.text()

    if admin_id == "" or password == "":

        QMessageBox.warning(
            login_window,
            "로그인",
            "아이디와 비밀번호를 입력해주세요."
        )

        return

    try:
        admin = auth.admin_login(admin_id, password)
    except DBError as error:

        QMessageBox.critical(
            login_window,
            "DB 오류",
            str(error)
        )

        return

    if admin is None:

        QMessageBox.warning(
            login_window,
            "로그인 실패",
            "아이디 또는 비밀번호가 올바르지 않습니다."
        )

        admin_password_input.clear()
        admin_password_input.setFocus()

        return

    current_admin = admin

    admin_password_input.clear()
    login_window.hide()

    show_admin_main()


# ============================================================
# 관리자 메인 : 전체 민원 목록
# ============================================================

def show_admin_main():

    global admin_main_window
    global status_filter
    global complaint_table
    global summary_label

    admin_main_window = QWidget()
    admin_main_window.setWindowTitle("기숙사 시설 관리 시스템 - 관리자")
    admin_main_window.resize(1000, 680)
    admin_main_window.setStyleSheet(APP_STYLE)

    layout = QVBoxLayout()
    layout.setContentsMargins(30, 30, 30, 25)
    layout.setSpacing(12)

    # --------------------------------------------------------
    # 상단 카드 : 제목 + 관리자 이름 + 로그아웃
    # --------------------------------------------------------

    header = QFrame()
    header.setObjectName("card")

    header_layout = QHBoxLayout()
    header_layout.setContentsMargins(25, 20, 25, 20)

    title_layout = QVBoxLayout()
    title_layout.setSpacing(4)

    title = QLabel("민원 관리")
    title.setObjectName("title")

    admin_label = QLabel(
        f"{current_admin['name']} 관리자님 ({current_admin['role']})"
    )
    admin_label.setObjectName("subtitle")

    title_layout.addWidget(title)
    title_layout.addWidget(admin_label)

    logout_button = QPushButton("로그아웃")
    logout_button.setObjectName("backButton")
    logout_button.clicked.connect(admin_logout)

    header_layout.addLayout(title_layout)
    header_layout.addStretch()
    header_layout.addWidget(logout_button)

    header.setLayout(header_layout)

    layout.addWidget(header)

    # --------------------------------------------------------
    # 처리 상태 거르기 + 새로고침 + 건수 요약
    # --------------------------------------------------------

    filter_layout = QHBoxLayout()
    filter_layout.setSpacing(10)

    filter_label = QLabel("처리 상태")
    filter_label.setObjectName("label")

    status_filter = QComboBox()
    status_filter.addItems(STATUS_FILTERS)
    status_filter.setFixedWidth(140)
    status_filter.currentIndexChanged.connect(
        lambda index: load_complaints()
    )

    refresh_button = QPushButton("새로고침")
    refresh_button.setObjectName("blueButton")
    refresh_button.setFixedSize(100, 40)
    refresh_button.clicked.connect(load_complaints)

    summary_label = QLabel()
    summary_label.setObjectName("subtitle")

    filter_layout.addWidget(filter_label)
    filter_layout.addWidget(status_filter)
    filter_layout.addWidget(refresh_button)
    filter_layout.addStretch()
    filter_layout.addWidget(summary_label)

    layout.addLayout(filter_layout)

    # --------------------------------------------------------
    # 민원 목록 표
    # --------------------------------------------------------

    complaint_table = QTableWidget(0, len(TABLE_HEADERS))
    complaint_table.setHorizontalHeaderLabels(TABLE_HEADERS)
    complaint_table.verticalHeader().setVisible(False)
    complaint_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    complaint_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    complaint_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    header_view = complaint_table.horizontalHeader()

    for column in range(len(TABLE_HEADERS)):
        header_view.setSectionResizeMode(
            column,
            QHeaderView.ResizeMode.ResizeToContents
        )

    # 민원 유형, 위치 열은 남는 폭을 나눠 가짐
    header_view.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
    header_view.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

    complaint_table.cellDoubleClicked.connect(
        lambda row, column: open_complaint_detail(row)
    )

    layout.addWidget(complaint_table)

    hint_label = QLabel(
        "목록을 두 번 클릭하면 상세 내용을 보고 처리 상태를 변경할 수 있습니다."
    )
    hint_label.setObjectName("subtitle")
    hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout.addWidget(hint_label)

    admin_main_window.setLayout(layout)

    load_complaints()

    admin_main_window.show()


# ============================================================
# 민원 목록 불러오기 (표 다시 채우기)
# ============================================================

def load_complaints():

    status = status_filter.currentText()

    if status == "전체":
        status = None

    try:
        rows = complaint.get_all_complaints(status)
    except DBError as error:

        QMessageBox.critical(
            admin_main_window,
            "DB 오류",
            str(error)
        )

        return

    complaint_table.setRowCount(0)

    for row in rows:

        row_index = complaint_table.rowCount()
        complaint_table.insertRow(row_index)

        values = [
            str(row["complaint_id"]),
            complaint.format_datetime(row["created_at"]),
            row["student_id"],
            row["student_name"],
            f"{row['category']} > {row['type_name']}",
            row["location_name"],
            row["status"],
        ]

        for column, value in enumerate(values):

            item = QTableWidgetItem(value)

            if column in (0, 6):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            complaint_table.setItem(row_index, column, item)

        # 번호 칸에 민원 번호 저장 (두 번 클릭 시 사용)
        complaint_table.item(row_index, 0).setData(
            Qt.ItemDataRole.UserRole,
            row["complaint_id"]
        )

        # 처리 상태 글자 색
        status_color = ui_detail.STATUS_COLORS.get(row["status"], "#202124")

        complaint_table.item(row_index, 6).setForeground(
            QBrush(QColor(status_color))
        )

    # 건수 요약
    if status is None:

        counts = [
            f"{name} {sum(1 for row in rows if row['status'] == name)}"
            for name in complaint.STATUS_LIST
        ]

        summary_label.setText(f"전체 {len(rows)}건  ·  " + "  ·  ".join(counts))

    else:

        summary_label.setText(f"{status} {len(rows)}건")


# ============================================================
# 민원 상세 + 처리 (상태 변경, 답변 등록)
# ============================================================

def open_complaint_detail(row):

    complaint_id = complaint_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

    try:
        detail = complaint.get_complaint_detail(complaint_id)
    except DBError as error:

        QMessageBox.critical(
            admin_main_window,
            "DB 오류",
            str(error)
        )

        return

    if detail is None:

        QMessageBox.warning(
            admin_main_window,
            "민원 상세",
            "민원을 찾을 수 없습니다."
        )

        load_complaints()

        return

    dialog, dialog_layout = ui_detail.create_detail_dialog(
        admin_main_window,
        detail,
        show_student=True
    )

    dialog.resize(560, 860)

    # --------------------------------------------------------
    # 처리하기 카드
    # --------------------------------------------------------

    process_card, process_layout = ui_detail.make_card("처리하기")

    status_row = QHBoxLayout()

    status_label = QLabel("처리 상태")
    status_label.setObjectName("label")
    status_label.setFixedWidth(80)

    status_combo = QComboBox()
    status_combo.addItems(complaint.STATUS_LIST)
    status_combo.setCurrentText(detail["status"])

    status_row.addWidget(status_label)
    status_row.addWidget(status_combo, 1)

    process_layout.addLayout(status_row)

    response_input = QTextEdit()
    response_input.setPlaceholderText(
        "학생에게 보낼 답변이나 처리 내용을 입력하세요. (선택)"
    )
    response_input.setFixedHeight(80)

    process_layout.addWidget(response_input)

    def save():

        try:
            success, message = complaint.update_status(
                complaint_id,
                current_admin["admin_id"],
                status_combo.currentText(),
                response_input.toPlainText()
            )
        except DBError as error:

            QMessageBox.critical(
                dialog,
                "처리 저장",
                str(error)
            )

            return

        if not success:

            QMessageBox.warning(
                dialog,
                "처리 저장",
                message
            )

            return

        QMessageBox.information(
            dialog,
            "처리 저장",
            message
        )

        dialog.accept()

        load_complaints()

    button_row = QHBoxLayout()

    close_button = QPushButton("닫기")
    close_button.setObjectName("backButton")
    close_button.clicked.connect(dialog.reject)

    save_button = QPushButton("저장")
    save_button.setObjectName("blueButton")
    save_button.setFixedSize(120, 42)
    save_button.clicked.connect(save)

    button_row.addStretch()
    button_row.addWidget(close_button)
    button_row.addWidget(save_button)

    process_layout.addLayout(button_row)

    dialog_layout.addWidget(process_card)

    dialog.exec()


# ============================================================
# 로그아웃 → 로그인 화면
# ============================================================

def admin_logout():

    global current_admin

    current_admin = None

    admin_main_window.close()

    admin_password_input.clear()
    login_window.show()
