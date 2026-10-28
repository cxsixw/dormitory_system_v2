-- ============================================================
-- 기숙사 시설 관리 시스템 DB 설계 (최종 목표, MySQL)
-- 테이블 7개
--   STUDENT, ADMIN            : 사용자
--   LOCATION, COMPLAINT_TYPE  : 기준 정보 (위치 목록, 민원 유형 목록)
--   COMPLAINT                 : 민원
--   REPORT_HISTORY            : 처리 이력·관리자 답변
--   ATTACHMENT                : 첨부 사진 (실제 파일은 서버 폴더에 저장)
-- ============================================================

CREATE DATABASE IF NOT EXISTS dormitory CHARACTER SET utf8mb4;
USE dormitory;

-- ------------------------------------------------------------
-- 위치 : 기숙사 방, 휴게실, 세탁실, 복도, 기타 시설
-- ------------------------------------------------------------
CREATE TABLE LOCATION (
    location_id    INT          NOT NULL AUTO_INCREMENT COMMENT '위치 번호',
    dorm_section   VARCHAR(10)  NOT NULL COMMENT '구분 (여/남/공용)',
    floor          TINYINT      NULL     COMMENT '층',
    place_type     VARCHAR(20)  NOT NULL COMMENT '장소 종류 (기숙사 방/휴게실/세탁실/복도/기타 시설)',
    room_no        VARCHAR(10)  NULL     COMMENT '호수 (기숙사 방일 때만)',
    location_name  VARCHAR(50)  NOT NULL COMMENT '화면 표시 이름 (예: 여 5층 세탁실)',
    PRIMARY KEY (location_id),
    UNIQUE KEY uq_location (dorm_section, floor, place_type, room_no)
) COMMENT='위치 정보';

-- ------------------------------------------------------------
-- 민원 유형 : 시설 신고 / 생활 불편 아래의 세부 문제 유형
-- ------------------------------------------------------------
CREATE TABLE COMPLAINT_TYPE (
    type_id        INT          NOT NULL AUTO_INCREMENT COMMENT '유형 번호',
    category       VARCHAR(20)  NOT NULL COMMENT '민원 유형 (시설 신고/생활 불편)',
    type_name      VARCHAR(30)  NOT NULL COMMENT '문제 유형 (전기·조명, 냉난방, 소음 등)',
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE COMMENT '사용 여부',
    PRIMARY KEY (type_id),
    UNIQUE KEY uq_type (category, type_name)
) COMMENT='민원 유형';

-- ------------------------------------------------------------
-- 학생
-- ------------------------------------------------------------
CREATE TABLE STUDENT (
    student_id     VARCHAR(20)  NOT NULL COMMENT '학번',
    name           VARCHAR(50)  NOT NULL COMMENT '이름',
    email          VARCHAR(100) NOT NULL COMMENT '이메일 (비밀번호 찾기에 사용)',
    phone          VARCHAR(20)  NULL     COMMENT '연락처',
    room_id        INT          NULL     COMMENT '본인 호실 (LOCATION)',
    password_hash  CHAR(64)     NOT NULL COMMENT '암호화된 비밀번호',
    salt           CHAR(32)     NOT NULL COMMENT '비밀번호 암호화용 salt',
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '가입 일시',
    PRIMARY KEY (student_id),
    UNIQUE KEY uq_student_email (email),
    CONSTRAINT fk_student_room FOREIGN KEY (room_id) REFERENCES LOCATION (location_id)
) COMMENT='학생 정보';

-- ------------------------------------------------------------
-- 관리자
-- ------------------------------------------------------------
CREATE TABLE ADMIN (
    admin_id       VARCHAR(20)  NOT NULL COMMENT '관리자 아이디',
    name           VARCHAR(50)  NOT NULL COMMENT '이름',
    email          VARCHAR(100) NULL     COMMENT '이메일',
    role           VARCHAR(20)  NOT NULL DEFAULT '일반' COMMENT '권한 (일반/최고 관리자)',
    is_active      BOOLEAN      NOT NULL DEFAULT TRUE COMMENT '계정 사용 여부',
    password_hash  CHAR(64)     NOT NULL COMMENT '암호화된 비밀번호',
    salt           CHAR(32)     NOT NULL COMMENT '비밀번호 암호화용 salt',
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '등록 일시',
    PRIMARY KEY (admin_id)
) COMMENT='관리자 정보';

-- ------------------------------------------------------------
-- 민원
-- ------------------------------------------------------------
CREATE TABLE COMPLAINT (
    complaint_id   INT          NOT NULL AUTO_INCREMENT COMMENT '민원 번호',
    student_id     VARCHAR(20)  NOT NULL COMMENT '신고한 학생',
    type_id        INT          NOT NULL COMMENT '민원 유형',
    location_id    INT          NOT NULL COMMENT '발생 위치',
    content        TEXT         NOT NULL COMMENT '상세 내용',
    status         VARCHAR(10)  NOT NULL DEFAULT '접수' COMMENT '처리 상태 (접수/확인/처리 중/완료)',
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '신고 일시',
    updated_at     DATETIME     NULL     COMMENT '최근 수정 일시',
    completed_at   DATETIME     NULL     COMMENT '처리 완료 일시',
    PRIMARY KEY (complaint_id),
    KEY idx_complaint_status (status),
    KEY idx_complaint_created (created_at),
    CONSTRAINT fk_complaint_student  FOREIGN KEY (student_id)  REFERENCES STUDENT (student_id),
    CONSTRAINT fk_complaint_type     FOREIGN KEY (type_id)     REFERENCES COMPLAINT_TYPE (type_id),
    CONSTRAINT fk_complaint_location FOREIGN KEY (location_id) REFERENCES LOCATION (location_id)
) COMMENT='민원 정보';

-- ------------------------------------------------------------
-- 처리 이력 : 상태가 바뀔 때마다 1줄씩 기록, 관리자 답변 포함
-- ------------------------------------------------------------
CREATE TABLE REPORT_HISTORY (
    history_id     INT          NOT NULL AUTO_INCREMENT COMMENT '이력 번호',
    complaint_id   INT          NOT NULL COMMENT '민원 번호',
    admin_id       VARCHAR(20)  NOT NULL COMMENT '처리한 관리자',
    prev_status    VARCHAR(10)  NULL     COMMENT '변경 전 상태',
    new_status     VARCHAR(10)  NOT NULL COMMENT '변경 후 상태',
    response_text  TEXT         NULL     COMMENT '관리자 답변',
    changed_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '처리 일시',
    PRIMARY KEY (history_id),
    CONSTRAINT fk_history_complaint FOREIGN KEY (complaint_id) REFERENCES COMPLAINT (complaint_id) ON DELETE CASCADE,
    CONSTRAINT fk_history_admin     FOREIGN KEY (admin_id)     REFERENCES ADMIN (admin_id)
) COMMENT='처리 이력';

-- ------------------------------------------------------------
-- 첨부파일 : 사진은 서버 uploads/complaints/<민원번호>/ 에 저장하고 경로만 기록
-- ------------------------------------------------------------
CREATE TABLE ATTACHMENT (
    attachment_id  INT          NOT NULL AUTO_INCREMENT COMMENT '첨부파일 번호',
    complaint_id   INT          NOT NULL COMMENT '민원 번호',
    original_name  VARCHAR(255) NOT NULL COMMENT '원래 파일 이름',
    stored_name    VARCHAR(255) NOT NULL COMMENT '서버에 저장된 파일 이름',
    file_path      VARCHAR(255) NOT NULL COMMENT '저장 경로',
    file_size      INT          NOT NULL COMMENT '파일 크기 (byte)',
    uploaded_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '업로드 일시',
    PRIMARY KEY (attachment_id),
    CONSTRAINT fk_attachment_complaint FOREIGN KEY (complaint_id) REFERENCES COMPLAINT (complaint_id) ON DELETE CASCADE
) COMMENT='첨부파일';
