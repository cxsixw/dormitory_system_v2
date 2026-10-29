# ============================================================
# ui_student.py
# 학생 화면 모음 : 메인 / 민원 접수 / 내 신고 내역 / 내 정보
# ============================================================

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QComboBox,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QFileDialog,
    QDialog,
    QLineEdit,
)

from PySide6.QtCore import Qt, QObject, QEvent, QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from styles import APP_STYLE

import auth
import complaint
import file_manager
import ui_detail
from db import DBError


# 로그인한 학생 정보 (show_main_window에서 채워짐)
# 예: {"student_id": "202511217", "name": "홍길동", "email": "a@b.com"}
current_student = None

# 로그아웃 후 로그인 화면으로 돌아가는 함수 (ui_login 에서 넘겨줌)
logout_callback = None

# 자동 로그아웃 시간 (초) - 시연할 때는 10 정도로 줄여서 보여주면 편함
AUTO_LOGOUT_SECONDS = 180


# ============================================================
# 자동 로그아웃
# 마우스 클릭/이동, 키보드 입력, 스크롤이 있을 때마다 타이머를 처음부터 다시 셈.
# 정해진 시간 동안 아무 입력이 없으면 자동으로 로그아웃한다.
# (공용 휴게실 PC에서 다음 사람이 앞사람 계정을 쓰지 않도록)
# ============================================================

ACTIVITY_EVENTS = (
    QEvent.Type.MouseButtonPress,
    QEvent.Type.MouseMove,
    QEvent.Type.KeyPress,
    QEvent.Type.Wheel,
)


class ActivityWatcher(QObject):

    def eventFilter(self, watched, event):

        if event.type() in ACTIVITY_EVENTS and idle_timer.isActive():
            idle_timer.start()   # 다시 처음부터 셈

        return False   # 원래 하던 동작은 그대로 진행


idle_timer = None
activity_watcher = None


def start_idle_timer():

    global idle_timer
    global activity_watcher

    if idle_timer is None:

        idle_timer = QTimer()
        idle_timer.setSingleShot(True)
        idle_timer.timeout.connect(auto_logout)

        activity_watcher = ActivityWatcher()
        QApplication.instance().installEventFilter(activity_watcher)

    idle_timer.setInterval(AUTO_LOGOUT_SECONDS * 1000)
    idle_timer.start()


def auto_logout():

    if current_student is None:
        return

    logout()

    if AUTO_LOGOUT_SECONDS >= 60:
        idle_text = f"{AUTO_LOGOUT_SECONDS // 60}분"
    else:
        idle_text = f"{AUTO_LOGOUT_SECONDS}초"

    QMessageBox.information(
        None,
        "자동 로그아웃",
        f"{idle_text} 동안 사용하지 않아 자동으로 로그아웃되었습니다."
    )


# ============================================================
# 로그아웃 : 열려 있는 학생 화면을 모두 닫고 로그인 화면으로
# ============================================================

def logout():

    global current_student

    current_student = None

    if idle_timer is not None:
        idle_timer.stop()

    # 열려 있는 창(상세 보기, 비밀번호 변경, 알림창 등) 닫기
    for _ in range(10):

        modal = QApplication.activeModalWidget()

        if modal is None:
            break

        modal.close()

    for name in ["report_window", "history_window", "info_window", "main_window"]:

        window = globals().get(name)

        if window is not None:
            window.close()

    if logout_callback is not None:
        logout_callback()


# ============================================================
# 학생 메인 화면
# ============================================================

def show_main_window(student, on_logout=None):

    global main_window
    global current_student
    global logout_callback

    # 로그인에 성공한 학생 정보 저장
    current_student = student
    logout_callback = on_logout

    # 자동 로그아웃 타이머 시작
    start_idle_timer()

    main_window = QWidget()
    main_window.setWindowTitle("기숙사 시설 관리 시스템")
    main_window.resize(520, 650)
    main_window.setStyleSheet(APP_STYLE)

    layout = QVBoxLayout()
    layout.setContentsMargins(35, 35, 35, 30)
    layout.setSpacing(15)

    # 상단
    header = QFrame()
    header.setObjectName("card")

    header_layout = QVBoxLayout()
    header_layout.setContentsMargins(25, 22, 25, 22)
    header_layout.setSpacing(5)

    title = QLabel("기숙사 시설 관리 시스템")
    title.setObjectName("title")

    student_label = QLabel(
        f"{current_student['name']}님, 안녕하세요."
    )
    student_label.setObjectName("subtitle")

    header_layout.addWidget(title)
    header_layout.addWidget(student_label)

    # 로그아웃 버튼 (오른쪽 위)
    logout_button = QPushButton("로그아웃")
    logout_button.setObjectName("backButton")
    logout_button.clicked.connect(logout)

    header_row = QHBoxLayout()
    header_row.setContentsMargins(0, 0, 18, 0)
    header_row.addLayout(header_layout)
    header_row.addStretch()
    header_row.addWidget(logout_button)

    header.setLayout(header_row)

    layout.addWidget(header)

    # 메뉴
    menu_title = QLabel("무엇을 도와드릴까요?")
    menu_title.setObjectName("sectionTitle")

    layout.addWidget(menu_title)

    # 민원 접수
    report_button = QPushButton(
        "📝  민원 접수\n"
        "      시설 문제나 생활 불편사항을 등록합니다."
    )

    report_button.setObjectName("menuButton")
    report_button.setFixedHeight(75)
    report_button.clicked.connect(show_report_window)

    # 내 신고 내역
    history_button = QPushButton(
        "📋  내 신고 내역\n"
        "      등록한 신고의 처리 상태를 확인합니다."
    )

    history_button.setObjectName("menuButton")
    history_button.setFixedHeight(75)
    history_button.clicked.connect(show_history_window)

    # 내 정보
    info_button = QPushButton(
        "👤  내 정보\n"
        "      학생 계정 정보를 확인합니다."
    )

    info_button.setObjectName("menuButton")
    info_button.setFixedHeight(75)
    info_button.clicked.connect(show_info_window)

    layout.addWidget(report_button)
    layout.addWidget(history_button)
    layout.addWidget(info_button)

    layout.addStretch()

    bottom_label = QLabel(
        "기숙사 생활 중 불편한 사항을 편리하게 신고하세요."
    )

    bottom_label.setObjectName("subtitle")
    bottom_label.setAlignment(Qt.AlignCenter)

    layout.addWidget(bottom_label)

    main_window.setLayout(layout)
    main_window.show()


# ============================================================
# 민원 접수 화면
# ============================================================

def show_report_window():

    main_window.hide()

    global report_window
    global problem_combo
    global location_combo
    global floor_combo
    global room_combo
    global floor_label
    global room_label
    global content_input
    global type_combo
    global photo_label
    global selected_photos

    # 이번 신고에 첨부할 사진 경로 목록
    selected_photos = []

    report_window = QWidget()
    report_window.setWindowTitle("민원 접수")
    report_window.resize(520, 780)
    report_window.setStyleSheet(APP_STYLE)

    layout = QVBoxLayout()
    layout.setContentsMargins(35, 30, 35, 25)
    layout.setSpacing(10)

    # 제목
    title = QLabel("민원 접수")
    title.setObjectName("title")
    title.setAlignment(Qt.AlignCenter)

    subtitle = QLabel(
        "시설 문제 또는 생활 불편사항을 등록해주세요."
    )
    subtitle.setObjectName("subtitle")
    subtitle.setAlignment(Qt.AlignCenter)

    layout.addWidget(title)
    layout.addWidget(subtitle)

    layout.addSpacing(10)

    # --------------------------------------------------------
    # 민원 유형
    # --------------------------------------------------------

    type_card = QFrame()
    type_card.setObjectName("card")

    type_layout = QVBoxLayout()
    type_layout.setContentsMargins(18, 16, 18, 16)
    type_layout.setSpacing(7)

    type_label = QLabel("민원 유형")
    type_label.setObjectName("label")

    type_combo = QComboBox()

    type_combo.addItems([
        "시설 신고",
        "생활 불편"
    ])

    type_layout.addWidget(type_label)
    type_layout.addWidget(type_combo)

    type_card.setLayout(type_layout)

    layout.addWidget(type_card)

    # --------------------------------------------------------
    # 문제 유형
    # --------------------------------------------------------

    problem_card = QFrame()
    problem_card.setObjectName("card")

    problem_layout = QVBoxLayout()
    problem_layout.setContentsMargins(18, 16, 18, 16)
    problem_layout.setSpacing(7)

    problem_label = QLabel("문제 유형")
    problem_label.setObjectName("label")

    problem_combo = QComboBox()

    facility_types = [
        "전기·조명",
        "냉난방",
        "수도",
        "도어락",
        "기타"
    ]

    living_types = [
        "인터넷(WIFI)",
        "카드키 오류",
        "소음",
        "위생",
        "공사",
        "기타 생활 불편"
    ]

    problem_combo.addItems(facility_types)

    type_combo.currentIndexChanged.connect(
        lambda index: update_problem_types(
            type_combo,
            facility_types,
            living_types
        )
    )

    problem_layout.addWidget(problem_label)
    problem_layout.addWidget(problem_combo)

    problem_card.setLayout(problem_layout)

    layout.addWidget(problem_card)

    # --------------------------------------------------------
    # 발생 위치
    # --------------------------------------------------------

    location_card = QFrame()
    location_card.setObjectName("card")

    location_layout = QVBoxLayout()
    location_layout.setContentsMargins(18, 16, 18, 16)
    location_layout.setSpacing(7)

    location_label = QLabel("발생 위치")
    location_label.setObjectName("label")

    location_combo = QComboBox()

    location_combo.addItems([
        "기숙사 방(여)",
        "기숙사 방(남)",
        "휴게실",
        "세탁실",
        "복도",
        "기타 시설"
    ])

    location_layout.addWidget(location_label)
    location_layout.addWidget(location_combo)

    # 층 / 호수
    floor_label = QLabel("층")
    floor_label.setObjectName("label")

    floor_combo = QComboBox()

    floor_combo.addItems([
        "층 선택",
        "4층",
        "5층",
        "6층",
        "7층",
        "8층",
        "9층",
        "10층"
    ])

    room_label = QLabel("호수")
    room_label.setObjectName("label")

    room_combo = QComboBox()
    room_combo.addItem("호수 선택")

    floor_room_layout = QHBoxLayout()
    floor_room_layout.setSpacing(8)

    floor_room_layout.addWidget(floor_label)
    floor_room_layout.addWidget(floor_combo)

    floor_room_layout.addSpacing(10)

    floor_room_layout.addWidget(room_label)
    floor_room_layout.addWidget(room_combo)

    location_layout.addLayout(floor_room_layout)

    location_card.setLayout(location_layout)

    layout.addWidget(location_card)

    floor_combo.currentIndexChanged.connect(
        lambda index: update_room_list(
            floor_combo,
            room_combo
        )
    )

    location_combo.currentIndexChanged.connect(
        lambda index: update_location_fields(location_combo)
    )

    # --------------------------------------------------------
    # 상세 내용
    # --------------------------------------------------------

    content_card = QFrame()
    content_card.setObjectName("card")

    content_layout = QVBoxLayout()
    content_layout.setContentsMargins(18, 16, 18, 16)
    content_layout.setSpacing(7)

    content_label = QLabel("상세 내용")
    content_label.setObjectName("label")

    content_input = QTextEdit()

    content_input.setPlaceholderText(
        "문제를 자세히 입력해주세요."
    )

    content_input.setFixedHeight(100)

    content_layout.addWidget(content_label)
    content_layout.addWidget(content_input)

    content_card.setLayout(content_layout)

    layout.addWidget(content_card)

    # 사진 첨부
    photo_button = QPushButton(
        "📷  사진 첨부"
    )

    photo_button.setObjectName("photoButton")
    photo_button.setFixedHeight(42)

    photo_button.clicked.connect(select_photos)

    layout.addWidget(photo_button)

    # 선택된 사진 표시
    photo_label = QLabel()
    photo_label.setObjectName("subtitle")
    photo_label.setWordWrap(True)

    layout.addWidget(photo_label)

    update_photo_label()

    # 신고 등록
    register_button = QPushButton(
        "신고 등록"
    )

    register_button.setObjectName("blueButton")
    register_button.setFixedHeight(46)

    register_button.clicked.connect(register_report)

    layout.addWidget(register_button)

    # 이전
    back_button = QPushButton(
        "← 이전"
    )

    back_button.setObjectName("backButton")

    back_button.clicked.connect(
        back_to_main_from_report
    )

    layout.addWidget(
        back_button,
        alignment=Qt.AlignCenter
    )

    report_window.setLayout(layout)

    update_location_fields(location_combo)

    report_window.show()


# ============================================================
# 문제 유형 변경
# ============================================================

def update_problem_types(
    type_combo,
    facility_types,
    living_types
):

    problem_combo.clear()

    if type_combo.currentText() == "시설 신고":
        problem_combo.addItems(facility_types)
    else:
        problem_combo.addItems(living_types)


# ============================================================
# 발생 위치 변경
# ============================================================

def update_location_fields(location_combo):

    if location_combo.currentText() in [
        "기숙사 방(여)",
        "기숙사 방(남)"
    ]:

        floor_label.show()
        floor_combo.show()

        room_label.show()
        room_combo.show()

    else:

        floor_label.hide()
        floor_combo.hide()

        room_label.hide()
        room_combo.hide()


# ============================================================
# 층 선택 → 호수 목록
# ============================================================

def update_room_list(
    floor_combo,
    room_combo
):

    room_combo.clear()

    floor = floor_combo.currentText()

    if floor == "층 선택":

        room_combo.addItem("호수 선택")
        return

    floor_number = int(
        floor.replace("층", "")
    )

    room_numbers = [
        f"{floor_number}01호",
        f"{floor_number}02호",
        f"{floor_number}03호",
        f"{floor_number}04호",
        f"{floor_number}05호",
        f"{floor_number}06호",
        f"{floor_number}07호",
        f"{floor_number}08호",
        f"{floor_number}09호",
        f"{floor_number}10호",
        f"{floor_number}11호",
        f"{floor_number}12호",
        f"{floor_number}13호",
        f"{floor_number}14호",
        f"{floor_number}15호",
        f"{floor_number}16호",
        f"{floor_number}17호",
        f"{floor_number}18호",
        f"{floor_number}19호",
        f"{floor_number}20호",
        f"{floor_number}21호",
        f"{floor_number}22호",
        f"{floor_number}23호",
        f"{floor_number}24호",
        f"{floor_number}25호",
        f"{floor_number}26호",
        f"{floor_number}27호",
        f"{floor_number}28호",
        f"{floor_number}29호",
        f"{floor_number}30호",
        f"{floor_number}31호",
    ]

    room_combo.addItem("호수 선택")
    room_combo.addItems(room_numbers)


# ============================================================
# 신고 등록 → DB(COMPLAINT, ATTACHMENT)에 저장
# ============================================================

def register_report():

    location = location_combo.currentText()
    content = content_input.toPlainText().strip()

    if location in [
        "기숙사 방(여)",
        "기숙사 방(남)"
    ]:

        if floor_combo.currentText() == "층 선택":

            QMessageBox.warning(
                report_window,
                "신고 등록",
                "발생 층을 선택해주세요."
            )

            return

        if room_combo.currentText() == "호수 선택":

            QMessageBox.warning(
                report_window,
                "신고 등록",
                "호수를 선택해주세요."
            )

            return

    if content == "":

        QMessageBox.warning(
            report_window,
            "신고 등록",
            "상세 내용을 입력해주세요."
        )

        return

    # 화면에서 고른 값 정리
    data = {
        "category": type_combo.currentText(),
        "problem_type": problem_combo.currentText(),
        "location": location,
        "floor": None,
        "room_no": None,
        "content": content,
    }

    if location in ["기숙사 방(여)", "기숙사 방(남)"]:
        # "5층" → 5,  "501호" → "501"
        data["floor"] = int(floor_combo.currentText().replace("층", ""))
        data["room_no"] = room_combo.currentText().replace("호", "")

    try:
        complaint_id = complaint.create_complaint(
            current_student["student_id"],
            data,
            selected_photos
        )
    except DBError as error:

        QMessageBox.critical(
            report_window,
            "신고 등록",
            str(error)
        )

        return

    QMessageBox.information(
        report_window,
        "신고 등록",
        f"신고가 등록되었습니다. (민원 번호 {complaint_id}번)\n"
        "'내 신고 내역'에서 처리 상태를 확인할 수 있습니다."
    )

    back_to_main_from_report()


# ============================================================
# 사진 선택 (jpg / jpeg / png, 최대 3장)
# ============================================================

def select_photos():

    global selected_photos

    files, _ = QFileDialog.getOpenFileNames(
        report_window,
        "첨부할 사진 선택",
        "",
        "이미지 파일 (*.jpg *.jpeg *.png)"
    )

    # 취소 → 기존 선택 유지
    if not files:
        return

    if len(files) > file_manager.MAX_PHOTO_COUNT:

        QMessageBox.warning(
            report_window,
            "사진 첨부",
            f"사진은 최대 {file_manager.MAX_PHOTO_COUNT}장까지 첨부할 수 있습니다."
        )

        return

    for path in files:

        error = file_manager.validate_image(path)

        if error is not None:

            QMessageBox.warning(
                report_window,
                "사진 첨부",
                error
            )

            return

    selected_photos = files

    update_photo_label()


def update_photo_label():

    if len(selected_photos) == 0:

        photo_label.setText(
            f"선택된 사진 없음 (jpg, png · 최대 {file_manager.MAX_PHOTO_COUNT}장)"
        )

    else:

        names = ", ".join(
            path.replace("\\", "/").split("/")[-1]
            for path in selected_photos
        )

        photo_label.setText(f"📎 {names} ({len(selected_photos)}장)")


# ============================================================
# 민원 접수 → 메인
# ============================================================

def back_to_main_from_report():

    report_window.close()

    # 자동 로그아웃된 뒤라면 메인 화면을 다시 열지 않음
    if current_student is not None:
        main_window.show()


# ============================================================
# 내 신고 내역 (DB에서 내가 등록한 신고만 조회)
# ============================================================

def show_history_window():

    main_window.hide()

    global history_window

    history_window = QWidget()
    history_window.setWindowTitle("내 신고 내역")
    history_window.resize(520, 650)
    history_window.setStyleSheet(APP_STYLE)

    layout = QVBoxLayout()

    layout.setContentsMargins(
        35,
        35,
        35,
        30
    )

    layout.setSpacing(12)

    # 제목 카드
    header = QFrame()
    header.setObjectName("card")

    header_layout = QVBoxLayout()

    header_layout.setContentsMargins(
        22,
        20,
        22,
        20
    )

    title = QLabel("내 신고 내역")
    title.setObjectName("title")

    subtitle = QLabel(
        "등록한 신고의 처리 상태를 확인할 수 있습니다."
    )

    subtitle.setObjectName("subtitle")

    header_layout.addWidget(title)
    header_layout.addWidget(subtitle)

    header.setLayout(header_layout)

    layout.addWidget(header)

    # 신고 목록
    history_list = QListWidget()

    try:
        rows = complaint.get_my_complaints(
            current_student["student_id"]
        )
    except DBError as error:

        QMessageBox.critical(
            main_window,
            "내 신고 내역",
            str(error)
        )

        rows = []

    if len(rows) == 0:

        empty_item = QListWidgetItem("아직 등록한 신고가 없습니다.")
        empty_item.setFlags(Qt.ItemFlag.NoItemFlags)

        history_list.addItem(empty_item)

    for row in rows:

        icon = "🏢" if row["category"] == "시설 신고" else "🏠"

        item = QListWidgetItem(
            f"{icon} {row['type_name']} · {row['location_name']}\n"
            f"처리 상태: {row['status']}     "
            f"신고일: {complaint.format_datetime(row['created_at'])}"
        )

        # 항목을 눌렀을 때 어떤 민원인지 알 수 있도록 번호 저장
        item.setData(Qt.ItemDataRole.UserRole, row["complaint_id"])

        history_list.addItem(item)

    history_list.itemClicked.connect(open_my_complaint)

    layout.addWidget(history_list)

    hint_label = QLabel("항목을 누르면 상세 내용과 관리자 답변을 볼 수 있습니다.")
    hint_label.setObjectName("subtitle")
    hint_label.setAlignment(Qt.AlignCenter)

    layout.addWidget(hint_label)

    layout.addStretch()

    # 메인으로
    back_button = QPushButton(
        "← 메인 화면으로"
    )

    back_button.setObjectName(
        "backButton"
    )

    back_button.clicked.connect(
        back_to_main_from_history
    )

    layout.addWidget(
        back_button,
        alignment=Qt.AlignCenter
    )

    history_window.setLayout(layout)

    history_window.show()


# ============================================================
# 신고 내역 항목 클릭 → 상세 보기
# ============================================================

def open_my_complaint(item):

    complaint_id = item.data(Qt.ItemDataRole.UserRole)

    if complaint_id is None:
        return

    try:
        detail = complaint.get_complaint_detail(complaint_id)
    except DBError as error:

        QMessageBox.critical(
            history_window,
            "신고 상세",
            str(error)
        )

        return

    if detail is None:

        QMessageBox.warning(
            history_window,
            "신고 상세",
            "신고 내용을 찾을 수 없습니다."
        )

        return

    dialog, dialog_layout = ui_detail.create_detail_dialog(
        history_window,
        detail
    )

    close_button = QPushButton("닫기")
    close_button.setObjectName("blueButton")
    close_button.setFixedHeight(44)
    close_button.clicked.connect(dialog.accept)

    dialog_layout.addWidget(close_button)

    dialog.exec()


# ============================================================
# 신고 내역 → 메인
# ============================================================

def back_to_main_from_history():

    history_window.close()

    # 자동 로그아웃된 뒤라면 메인 화면을 다시 열지 않음
    if current_student is not None:
        main_window.show()


# ============================================================
# 내 정보
# ============================================================

def show_info_window():

    main_window.hide()

    global info_window

    info_window = QWidget()
    info_window.setWindowTitle("내 정보")
    info_window.resize(520, 650)
    info_window.setStyleSheet(APP_STYLE)

    layout = QVBoxLayout()

    layout.setContentsMargins(
        35,
        35,
        35,
        30
    )

    layout.setSpacing(12)

    # 프로필 카드
    profile_card = QFrame()
    profile_card.setObjectName("card")

    profile_layout = QVBoxLayout()

    profile_layout.setContentsMargins(
        25,
        25,
        25,
        25
    )

    profile_layout.setSpacing(7)

    profile_icon = QLabel("👤")

    profile_icon.setAlignment(
        Qt.AlignCenter
    )

    profile_icon.setFont(
        QFont("Arial", 38)
    )

    title = QLabel("내 정보")
    title.setObjectName("title")
    title.setAlignment(Qt.AlignCenter)

    subtitle = QLabel(
        "학생 계정 정보를 확인할 수 있습니다."
    )

    subtitle.setObjectName("subtitle")
    subtitle.setAlignment(Qt.AlignCenter)

    profile_layout.addWidget(profile_icon)
    profile_layout.addWidget(title)
    profile_layout.addWidget(subtitle)

    profile_card.setLayout(profile_layout)

    layout.addWidget(profile_card)

    # 계정 정보
    info_card = QFrame()
    info_card.setObjectName("card")

    info_layout = QVBoxLayout()

    info_layout.setContentsMargins(
        22,
        20,
        22,
        20
    )

    info_layout.setSpacing(7)

    account_title = QLabel("계정 정보")
    account_title.setObjectName("sectionTitle")

    info_layout.addWidget(account_title)

    info_layout.addSpacing(5)

    # 학번
    id_label = QLabel("학번")
    id_label.setObjectName("label")

    id_value = QLabel(
        current_student["student_id"]
    )

    id_value.setObjectName("value")

    info_layout.addWidget(id_label)
    info_layout.addWidget(id_value)

    info_layout.addSpacing(8)

    # 이름
    name_label = QLabel("이름")
    name_label.setObjectName("label")

    name_value = QLabel(
        current_student["name"]
    )

    name_value.setObjectName("value")

    info_layout.addWidget(name_label)
    info_layout.addWidget(name_value)

    info_layout.addSpacing(8)

    # 이메일
    email_label = QLabel("이메일")
    email_label.setObjectName("label")

    email_value = QLabel(
        current_student["email"]
    )

    email_value.setObjectName("value")

    info_layout.addWidget(email_label)
    info_layout.addWidget(email_value)

    info_card.setLayout(info_layout)

    layout.addWidget(info_card)

    # 계정 관리
    account_card = QFrame()
    account_card.setObjectName("card")

    account_layout = QVBoxLayout()

    account_layout.setContentsMargins(
        22,
        18,
        22,
        18
    )

    account_title = QLabel("계정 관리")
    account_title.setObjectName("sectionTitle")

    account_layout.addWidget(account_title)

    password_button = QPushButton(
        "🔑  비밀번호 변경"
    )

    password_button.setObjectName(
        "menuButton"
    )

    password_button.setFixedHeight(50)

    password_button.clicked.connect(show_password_dialog)

    account_layout.addWidget(password_button)

    account_card.setLayout(account_layout)

    layout.addWidget(account_card)

    layout.addStretch()

    # 메인으로
    back_button = QPushButton(
        "← 메인 화면으로"
    )

    back_button.setObjectName(
        "backButton"
    )

    back_button.clicked.connect(
        back_to_main_from_info
    )

    layout.addWidget(
        back_button,
        alignment=Qt.AlignCenter
    )

    info_window.setLayout(layout)

    info_window.show()


# ============================================================
# 비밀번호 변경 창
# ============================================================

def show_password_dialog():

    dialog = QDialog(info_window)
    dialog.setWindowTitle("비밀번호 변경")
    dialog.resize(420, 430)
    dialog.setStyleSheet(APP_STYLE)

    layout = QVBoxLayout()
    layout.setContentsMargins(35, 30, 35, 25)
    layout.setSpacing(8)

    title = QLabel("비밀번호 변경")
    title.setObjectName("title")
    title.setAlignment(Qt.AlignCenter)

    subtitle = QLabel(
        f"새 비밀번호는 {auth.MIN_PASSWORD_LENGTH}자 이상 입력해주세요."
    )
    subtitle.setObjectName("subtitle")
    subtitle.setAlignment(Qt.AlignCenter)

    layout.addWidget(title)
    layout.addWidget(subtitle)

    layout.addSpacing(10)

    inputs = []

    for label_text in ["현재 비밀번호", "새 비밀번호", "새 비밀번호 확인"]:

        label = QLabel(label_text)
        label.setObjectName("label")

        line_edit = QLineEdit()
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        line_edit.setFixedHeight(42)

        layout.addWidget(label)
        layout.addWidget(line_edit)

        inputs.append(line_edit)

    current_input, new_input, confirm_input = inputs

    def submit():

        try:
            success, message = auth.change_password(
                current_student["student_id"],
                current_input.text(),
                new_input.text(),
                confirm_input.text()
            )
        except DBError as error:

            QMessageBox.critical(
                dialog,
                "비밀번호 변경",
                str(error)
            )

            return

        if not success:

            QMessageBox.warning(
                dialog,
                "비밀번호 변경",
                message
            )

            return

        QMessageBox.information(
            dialog,
            "비밀번호 변경",
            message
        )

        dialog.accept()

    # 엔터 → 다음 칸, 마지막 칸에서 엔터 → 변경
    current_input.returnPressed.connect(new_input.setFocus)
    new_input.returnPressed.connect(confirm_input.setFocus)
    confirm_input.returnPressed.connect(submit)

    layout.addSpacing(10)

    change_button = QPushButton("변경하기")
    change_button.setObjectName("blueButton")
    change_button.setFixedHeight(46)
    change_button.clicked.connect(submit)

    cancel_button = QPushButton("취소")
    cancel_button.setObjectName("backButton")
    cancel_button.clicked.connect(dialog.reject)

    layout.addWidget(change_button)
    layout.addWidget(cancel_button, alignment=Qt.AlignCenter)

    dialog.setLayout(layout)

    current_input.setFocus()

    dialog.exec()


# ============================================================
# 내 정보 → 메인
# ============================================================

def back_to_main_from_info():

    info_window.close()

    # 자동 로그아웃된 뒤라면 메인 화면을 다시 열지 않음
    if current_student is not None:
        main_window.show()