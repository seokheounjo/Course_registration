-- schema.sql 파일 내용 수정
-- 이미 컬럼이 존재하는 경우 오류가 발생하지 않도록 IF NOT EXISTS 추가
ALTER TABLE subjects ADD COLUMN IF NOT EXISTS target_grade VARCHAR(10) DEFAULT '전체';