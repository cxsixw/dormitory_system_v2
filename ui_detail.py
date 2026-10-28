# ============================================================
# ui_detail.py
# 신고 상세 화면 (학생 '내 신고 내역'과 관리자 프로그램에서 같이 사용)
# 신고 정보 / 상세 내용 / 첨부 사진 / 처리 이력·관리자 답변
# ============================================================

from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
)

from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QPixmap, QIcon, QDesktopServices

from styles import APP_STYLE

import file_manager
from complaint import format_datetime


# 처리 상태별 글자 색
STATUS_COLORS = {
    "접수": "#D93025",
    "확인": "#E37400",
    "처리 중": "#1976D2",
    "완료": "#188038",
}


# ============================================================
# 제목이 있는 카드 하나 만들기 → (카드, 카드 안 레이아웃)
# ============================================================

def make_card(title_text):

    card = QFrame()
    card.setObjectName("card")

    card_layout = QVBoxLayout()
    card_layout.setContentsMargins(18, 16, 18, 16)
    card_layout.setSpacing(8)

    title = QLabel(title_text)
    title.setObjectName("sectionTitle")

    card_layout.addWidget(title)

    card.setLayout(card_layout)

    return card, card_layout


# ============================================================
# "항목   값" 한 줄
# ============================================================

def add_info_row(card_layout, label_text, value_text):

    row = QHBoxLayout()

    label = QLabel(label_text)
    label.setObjectName("label")
    label.setFixedWidth(80)

    value = QLabel(value_text)
    value.setWordWrap(True)

    row.addWidget(label)
    row.addWidget(value, 1)

    card_layout.addLayout(row)


# ============================================================
# 사진을 기본 사진 뷰어로 크게 열기
# ============================================================

def open_photo(path):

    QDesktopServices.openUrl(QUrl.fromLocalFile(path))


# ============================================================
# 신고 상세 창 만들기
# 결과 : (창, 창의 바깥 레이아웃)
#   - 바깥 레이아웃 아래쪽에 버튼 등을 더 붙일 수 있다. (관리자 처리 영역)
#   - 화면에 띄우는 건 호출한 쪽에서 dialog.exec()
# ============================================================

def create_detail_dialog(parent, detail, show_student=False):

    dialog = QDialog(parent)
    dialog.setWindowTitle(f"신고 상세 - {detail['complaint_id']}번")
    dialog.resize(540, 720)
    dialog.setStyleSheet(APP_STYLE)

    outer_layout = QVBoxLayout()
    outer_layout.setContentsMargins(25, 25, 25, 20)
    outer_layout.setSpacing(12)

    # 내용이 길어질 수 있으므로 스크롤 영역 안에 배치
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)

    content = QWidget()

    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 8, 0)
    layout.setSpacing(12)

    # --------------------------------------------------------
    # 제목 + 처리 상태
    # --------------------------------------------------------

    title = QLabel(f"{detail['type_name']} · {detail['location_name']}")
    title.setObjectName("title")
    title.setWordWrap(True)

    status_label = QLabel(f"처리 상태: {detail['status']}")
    status_color = STATUS_COLORS.get(detail["status"], "#202124")
    status_label.setStyleSheet(
        f"color: {status_color}; font-size: 15px; font-weight: bold;"
    )

    layout.addWidget(title)
    layout.addWidget(status_label)

    # --------------------------------------------------------
    # 신고 정보
    # --------------------------------------------------------

    info_card, info_layout = make_card("신고 정보")

    add_info_row(info_layout, "민원 번호", f"{detail['complaint_id']}번")

    if show_student:
        add_info_row(
            info_layout,
            "신고자",
            f"{detail['student_name']} ({detail['student_id']})"
        )

    add_info_row(
        info_layout,
        "민원 유형",
        f"{detail['category']} > {detail['type_name']}"
    )
    add_info_row(info_layout, "발생 위치", detail["location_name"])
    add_info_row(info_layout, "신고 일시", format_datetime(detail["created_at"]))

    if detail["completed_at"] is not None:
        add_info_row(info_layout, "완료 일시", format_datetime(detail["completed_at"]))

    layout.addWidget(info_card)

    # --------------------------------------------------------
    # 상세 내용
    # --------------------------------------------------------

    content_card, content_layout = make_card("상세 내용")

    content_text = QLabel(detail["content"])
    content_text.setWordWrap(True)
    content_text.setTextInteractionFlags(
        Qt.TextInteractionFlag.TextSelectableByMouse
    )

    content_layout.addWidget(content_text)

    layout.addWidget(content_card)

    # --------------------------------------------------------
    # 첨부 사진
    # --------------------------------------------------------

    attachments = detail["attachments"]

    photo_card, photo_layout = make_card(f"첨부 사진 ({len(attachments)}장)")

    if len(attachments) == 0:

        no_photo = QLabel("첨부된 사진이 없습니다.")
        no_photo.setObjectName("subtitle")

        photo_layout.addWidget(no_photo)

    else:

        photo_row = QHBoxLayout()
        photo_row.setSpacing(10)

        for attachment in attachments:

            path = file_manager.get_absolute_path(attachment["file_path"])
            pixmap = QPixmap(path)

            # 사진 파일이 지워졌거나 다른 PC에서 실행한 경우
            if pixmap.isNull():

                missing = QLabel("사진 파일을\n찾을 수 없음")
                missing.setObjectName("value")
                missing.setAlignment(Qt.AlignmentFlag.AlignCenter)
                missing.setFixedSize(130, 130)

                photo_row.addWidget(missing)
                continue

            photo_button = QPushButton()
            photo_button.setObjectName("photoButton")
            photo_button.setFixedSize(130, 130)
            photo_button.setIcon(QIcon(pixmap))
            photo_button.setIconSize(QSize(104, 104))
            photo_button.setToolTip(attachment["original_name"])

            photo_button.clicked.connect(
                lambda checked=False, photo_path=path: open_photo(photo_path)
            )

            photo_row.addWidget(photo_button)

        photo_row.addStretch()

        photo_layout.addLayout(photo_row)

        photo_hint = QLabel("사진을 누르면 크게 볼 수 있습니다.")
        photo_hint.setObjectName("subtitle")

        photo_layout.addWidget(photo_hint)

    layout.addWidget(photo_card)

    # --------------------------------------------------------
    # 처리 이력 · 관리자 답변
    # --------------------------------------------------------

    history = detail["history"]

    history_card, history_layout = make_card("처리 이력 · 관리자 답변")

    if len(history) == 0:

        no_history = QLabel("아직 처리 내역이 없습니다. (관리자 확인 대기)")
        no_history.setObjectName("subtitle")

        history_layout.addWidget(no_history)

    else:

        for record in history:

            prev_status = record["prev_status"] or "-"

            line = QLabel(
                f"{format_datetime(record['changed_at'])}   "
                f"{prev_status} → {record['new_status']}   "
                f"({record['admin_name']})"
            )
            line.setObjectName("label")

            history_layout.addWidget(line)

            if record["response_text"]:

                response = QLabel(record["response_text"])
                response.setObjectName("value")
                response.setWordWrap(True)

                history_layout.addWidget(response)

    layout.addWidget(history_card)

    layout.addStretch()

    content.setLayout(layout)
    scroll.setWidget(content)

    outer_layout.addWidget(scroll)

    dialog.setLayout(outer_layout)

    return dialog, outer_layout
