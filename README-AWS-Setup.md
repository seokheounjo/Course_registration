# AWS 배포 가이드

이 가이드는 Course Registration 애플리케이션을 AWS에 배포하는 방법을 설명합니다.

## 사전 요구사항

1. AWS CLI 설치 및 구성
2. GitHub 계정 및 리포지토리
3. Docker (로컬 테스트용)

## 배포 단계

### 1. AWS 인프라 설정

```bash
# 스크립트 실행 권한 부여
chmod +x aws-deploy.sh

# AWS 인프라 생성
./aws-deploy.sh
```

이 스크립트는 다음을 생성합니다:
- ECR 리포지토리 (Docker 이미지 저장)
- EC2 인스턴스 (t2.micro - Free Tier)
- RDS MySQL 인스턴스 (db.t3.micro - Free Tier)
- Security Groups (보안 설정)
- Key Pair (SSH 접속용)

### 2. GitHub Secrets 설정

스크립트 실행 후 출력되는 정보를 GitHub 리포지토리의 Settings > Secrets and variables > Actions에 추가:

- `AWS_ACCESS_KEY_ID`: AWS 액세스 키
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 키
- `EC2_SSH_KEY`: SSH 키 파일 내용
- `EC2_HOSTNAME`: EC2 인스턴스 공용 IP
- `DB_HOST`: RDS 엔드포인트
- `DB_PORT`: 3306
- `DB_NAME`: registrationdb
- `DB_USERNAME`: admin
- `DB_PASSWORD`: RDS 콘솔에서 확인

### 3. 애플리케이션 배포

1. 코드를 GitHub에 푸시:
```bash
git add .
git commit -m "Add AWS deployment configuration"
git push origin main
```

2. GitHub Actions가 자동으로 실행되어 배포됩니다.

### 4. 접속 확인

배포 완료 후 `http://[EC2-PUBLIC-IP]`로 접속하여 애플리케이션 확인

## 사용된 AWS 서비스 (Free Tier)

### EC2
- 인스턴스: t2.micro
- 750시간/월 무료

### RDS
- 인스턴스: db.t3.micro
- 스토리지: 20GB
- 750시간/월 무료

### ECR
- 500MB 스토리지 무료

## 로컬 테스트

Docker로 로컬 테스트:

```bash
# 이미지 빌드
docker build -t course-registration .

# MySQL 컨테이너 실행
docker run -d --name mysql-test \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=registrationdb \
  -p 3306:3306 mysql:8.0

# 애플리케이션 실행
docker run -d --name app-test \
  --link mysql-test:mysql \
  -e SPRING_PROFILES_ACTIVE=prod \
  -e DB_HOST=mysql \
  -e DB_PASSWORD=password \
  -p 8087:8087 course-registration
```

## 비용 최적화

1. 사용하지 않을 때 EC2 인스턴스 중지
2. RDS 인스턴스는 중지 불가하므로 필요시 삭제 후 재생성
3. ECR 이미지 정기적으로 정리

## 트러블슈팅

### 일반적인 문제

1. **DB 연결 실패**: Security Group 설정 확인
2. **Docker 빌드 실패**: Dockerfile 경로 및 권한 확인
3. **GitHub Actions 실패**: Secrets 설정 확인

### 로그 확인

```bash
# EC2 접속
ssh -i course-registration-key.pem ec2-user@[PUBLIC-IP]

# Docker 로그 확인
docker logs course-registration
```

## 정리

리소스 삭제:

```bash
# EC2 인스턴스 종료
aws ec2 terminate-instances --instance-ids [INSTANCE-ID]

# RDS 인스턴스 삭제
aws rds delete-db-instance --db-instance-identifier course-registration-db --skip-final-snapshot
```