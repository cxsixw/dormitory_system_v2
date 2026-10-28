# 기숙사 시설 관리 시스템

창업프로젝트 I — PySide6 + MySQL 기반 기숙사 시설 민원 관리 프로그램

## 실행 방법

```bash
pip install PySide6 pymysql
python main.py        # 학생 프로그램 (각 층 휴게실 PC)
python admin_main.py  # 관리자 프로그램 (관리자 PC)
```

## 실행 전 준비

1. MySQL Workbench에서 `schema.sql`을 실행해 `dormitory` DB와 테이블 7개를 만든다.
2. `db_config.py`의 `password`를 MySQL root 비밀번호로 수정한다. (양식: `db_config_example.py`)
3. 관리자 프로그램을 처음 실행하면 최초 관리자 계정 등록 창이 뜬다.

## 주요 기능

| 구분 | 기능 |
|---|---|
| 학생 | 회원가입, 로그인(엔터 지원), 민원 접수(사진 최대 3장), 내 신고 내역·상세·관리자 답변 확인, 비밀번호 변경 |
| 관리자 | 최초 관리자 등록, 관리자 로그인, 전체 민원 목록·처리 상태별 보기, 민원 상세·사진 확인, 처리 상태 변경·답변 등록 |

## 파일 구성

| 파일 | 역할 |
|---|---|
| `main.py` | 학생 프로그램 시작 |
| `admin_main.py` | 관리자 프로그램 시작 |
| `ui_login.py` | 학생 로그인, 회원가입 화면 |
| `ui_student.py` | 학생 메인, 민원 접수, 내 신고 내역, 내 정보·비밀번호 변경 화면 |
| `ui_admin.py` | 관리자 로그인·등록, 민원 목록, 처리 화면 |
| `ui_detail.py` | 신고 상세 화면 (학생·관리자 공용) |
| `styles.py` | 모든 화면 공통 스타일(QSS) |
| `auth.py` | 학생·관리자 계정 (가입, 로그인, 비밀번호 변경) |
| `complaint.py` | 민원 저장·조회, 처리 상태 변경 |
| `file_manager.py` | 첨부 사진 검사·저장 |
| `db.py` | MySQL 연결, SQL 실행, 트랜잭션 |
| `db_config.py` | MySQL 접속 정보 (깃허브에 올리지 않음) |
| `schema.sql` | DB 생성 및 테이블 7개 생성 SQL |

## 데이터 저장 방식

- 계정, 민원, 처리 이력은 MySQL `dormitory` DB에 저장한다.
- 비밀번호는 salt + PBKDF2-SHA256 해시로 저장한다.
- 첨부 사진은 `uploads/complaints/<민원번호>/`에 저장하고, DB(`ATTACHMENT`)에는 파일명과 경로만 기록한다.
