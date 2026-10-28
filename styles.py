# ============================================================
# styles.py
# 모든 화면에서 같이 쓰는 공통 스타일(QSS)
# ============================================================

APP_STYLE = """
    QWidget {
        background-color: #F5F7FA;
        color: #202124;
        font-family: "Malgun Gothic";
    }

    QLabel {
        background-color: transparent;
    }

    QFrame#card {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
    }

    QLabel#title {
        color: #202124;
        font-size: 24px;
        font-weight: bold;
    }

    QLabel#subtitle {
        color: #7A7F87;
        font-size: 13px;
    }

    QLabel#sectionTitle {
        color: #202124;
        font-size: 16px;
        font-weight: bold;
    }

    QLabel#label {
        color: #454A52;
        font-size: 13px;
        font-weight: bold;
    }

    QPushButton#primaryButton {
        background-color: #333333;
        color: white;
        border: none;
        border-radius: 9px;
        padding: 12px;
        font-size: 14px;
        font-weight: bold;
    }

    QPushButton#primaryButton:hover {
        background-color: #222222;
    }

    QPushButton#blueButton {
        background-color: #1976D2;
        color: white;
        border: none;
        border-radius: 9px;
        padding: 12px;
        font-size: 14px;
        font-weight: bold;
    }

    QPushButton#blueButton:hover {
        background-color: #1565C0;
    }

    QPushButton#menuButton {
        background-color: white;
        color: #202124;
        border: 1px solid #E1E4E8;
        border-radius: 12px;
        padding: 16px;
        font-size: 15px;
        text-align: left;
    }

    QPushButton#menuButton:hover {
        background-color: #F8FAFC;
        border: 1px solid #B8C0CA;
    }

    QPushButton#subButton {
        background-color: transparent;
        color: #6B7078;
        border: none;
        font-size: 13px;
        padding: 6px;
    }

    QPushButton#subButton:hover {
        color: #1976D2;
    }

    QPushButton#backButton {
        background-color: transparent;
        color: #6B7078;
        border: none;
        font-size: 13px;
        padding: 6px;
    }

    QPushButton#backButton:hover {
        color: #202124;
    }

    QLineEdit {
        background-color: white;
        color: #202124;
        border: 1px solid #D9DDE3;
        border-radius: 9px;
        padding: 11px;
        font-size: 14px;
    }

    QLineEdit:focus {
        border: 2px solid #1976D2;
    }

    QComboBox {
        background-color: white;
        color: #202124;
        border: 1px solid #D9DDE3;
        border-radius: 9px;
        padding: 10px;
        font-size: 14px;
    }

    QComboBox:focus {
        border: 1px solid #1976D2;
    }

    QTextEdit {
        background-color: white;
        color: #202124;
        border: 1px solid #D9DDE3;
        border-radius: 9px;
        padding: 10px;
        font-size: 14px;
    }

    QTextEdit:focus {
        border: 1px solid #1976D2;
    }

    QPushButton#photoButton {
        background-color: #F8F9FB;
        color: #555B64;
        border: 1px dashed #C8CDD4;
        border-radius: 9px;
        padding: 10px;
        font-size: 13px;
    }

    QPushButton#photoButton:hover {
        background-color: #F1F5F9;
        border: 1px dashed #9CA3AF;
    }

    QLabel#value {
        background-color: #F8F9FB;
        color: #4B5058;
        border: 1px solid #E3E6EA;
        border-radius: 9px;
        padding: 11px;
        font-size: 14px;
    }

    QListWidget {
        background-color: white;
        border: 1px solid #E1E4E8;
        border-radius: 12px;
        padding: 5px;
        font-size: 14px;
    }

    QListWidget::item {
        padding: 17px;
        border-bottom: 1px solid #EEEEEE;
    }

    QListWidget::item:hover {
        background-color: #F8FAFC;
    }

    QListWidget::item:selected {
        background-color: #EEF5FC;
        color: #202124;
    }

    /* 관리자 프로그램 : 민원 목록 표 */
    QTableWidget {
        background-color: white;
        border: 1px solid #E1E4E8;
        border-radius: 12px;
        gridline-color: #EEF0F3;
        font-size: 13px;
        selection-background-color: #EEF5FC;
        selection-color: #202124;
    }

    QHeaderView::section {
        background-color: #F8F9FB;
        color: #454A52;
        border: none;
        border-bottom: 1px solid #E1E4E8;
        padding: 8px;
        font-size: 13px;
        font-weight: bold;
    }

    QScrollArea {
        border: none;
    }
"""
