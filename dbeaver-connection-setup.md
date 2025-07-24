# DBeaver PostgreSQL 연결 설정 가이드

## 방법 1: Docker PostgreSQL 연결 (권장)

### 연결 정보
- **호스트**: `localhost`
- **포트**: `5432`
- **데이터베이스**: `postgres`
- **사용자명**: `postgres`
- **비밀번호**: `123456789`

### DBeaver 연결 단계

1. **DBeaver 실행**
2. **새 연결 생성**
   - `Database` → `New Database Connection`
   - PostgreSQL 선택

3. **연결 설정**
   ```
   Host: localhost
   Port: 5432
   Database: postgres
   Username: postgres
   Password: 123456789
   ```

4. **테스트 연결**
   - `Test Connection` 버튼 클릭
   - 성공 메시지 확인

5. **연결 완료**
   - `Finish` 클릭

### 데이터베이스 확인
```sql
-- 현재 데이터베이스 목록 확인
SELECT datname FROM pg_database;

-- pgvector 확장 확인
SELECT * FROM pg_extension WHERE extname = 'vector';

-- documents 테이블 확인
SELECT * FROM documents;
```

## 방법 2: 로컬 PostgreSQL 설치 (Windows)

### 1. PostgreSQL 설치
```bash
# Chocolatey 사용 (권장)
choco install postgresql

# 또는 공식 웹사이트에서 다운로드
# https://www.postgresql.org/download/windows/
```

### 2. 환경 변수 설정
```bash
# PostgreSQL bin 폴더를 PATH에 추가
# 일반적으로: C:\Program Files\PostgreSQL\{version}\bin
```

### 3. 서비스 시작
```bash
# PostgreSQL 서비스 시작
net start postgresql-x64-15

# 또는 수동으로 시작
pg_ctl -D "C:\Program Files\PostgreSQL\15\data" start
```

### 4. 사용자 및 데이터베이스 생성
```sql
-- PostgreSQL에 접속
psql -U postgres

-- 새 사용자 생성
CREATE USER postgres WITH PASSWORD 'postgres';

-- 데이터베이스 생성
CREATE DATABASE post_prac WITH ENCODING 'UTF8';

-- 권한 부여
ALTER DATABASE post_prac OWNER TO postgres;
GRANT ALL PRIVILEGES ON DATABASE post_prac TO postgres;

-- pgvector 확장 설치 (선택사항)
CREATE EXTENSION IF NOT EXISTS vector;
```

## DBeaver 추가 설정

### 1. 드라이버 설정
- PostgreSQL 드라이버가 자동으로 설치됨
- 필요시 수동으로 드라이버 다운로드 가능

### 2. 연결 풀 설정
```
Max connections: 10
Connection timeout: 30
Idle timeout: 600
```

### 3. SQL 편집기 설정
- 자동 완성 활성화
- 구문 강조 설정
- 실행 계획 보기 활성화

## 유용한 SQL 쿼리

### 기본 확인 쿼리
```sql
-- 버전 확인
SELECT version();

-- 현재 사용자 확인
SELECT current_user;

-- 현재 데이터베이스 확인
SELECT current_database();

-- 테이블 목록 확인
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- 스키마 목록 확인
SELECT schema_name FROM information_schema.schemata;
```

### pgvector 관련 쿼리 (Docker 버전)
```sql
-- 벡터 확장 확인
SELECT * FROM pg_extension WHERE extname = 'vector';

-- documents 테이블 구조 확인
\d documents

-- 샘플 데이터 조회
SELECT * FROM documents;
```

## 문제 해결

### 연결 오류
1. **포트 확인**: `netstat -an | findstr 5432`
2. **방화벽 설정**: Windows 방화벽에서 5432 포트 허용
3. **서비스 상태**: `services.msc`에서 PostgreSQL 서비스 확인

### 권한 오류
```sql
-- 사용자 권한 확인
SELECT usename, usesuper, usecreatedb FROM pg_user;

-- 데이터베이스 권한 확인
SELECT datname, datacl FROM pg_database;
```

### Docker 관련
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs db

# 컨테이너 재시작
docker-compose restart db
``` 