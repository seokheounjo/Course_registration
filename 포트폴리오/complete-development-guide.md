# 🎓 수강신청 시스템 CI/CD 완전 개발 가이드

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [개발 환경 준비](#개발-환경-준비)
3. [Spring Boot 애플리케이션 개발](#spring-boot-애플리케이션-개발)
4. [Docker 컨테이너화](#docker-컨테이너화)
5. [AWS 인프라 구축](#aws-인프라-구축)
6. [CI/CD 파이프라인 구축](#cicd-파이프라인-구축)
7. [EKS + ArgoCD 배포](#eks--argocd-배포)
8. [문제해결 및 디버깅](#문제해결-및-디버깅)
9. [모니터링 및 운영](#모니터링-및-운영)

---

## 프로젝트 개요

### 🎯 목표
- Spring Boot 기반 수강신청 웹 시스템 개발
- GitHub Actions CI/CD 파이프라인 구축
- AWS 클라우드 인프라 배포 (EC2 + EKS)
- ArgoCD GitOps 기반 지속적 배포

### 📅 개발 일정
- **Day 1-2**: Spring Boot 애플리케이션 개발
- **Day 3**: Docker 컨테이너화 및 CI/CD 구축
- **Day 4**: AWS 인프라 구축 및 배포
- **Day 5**: EKS + ArgoCD 고도화 및 최적화

### 🛠️ 기술 스택
```
Backend:     Java 17, Spring Boot 3.1.2, JPA, Mustache
Database:    MySQL (AWS RDS)
Container:   Docker, DockerHub
CI/CD:       GitHub Actions, ArgoCD
Cloud:       AWS EC2, EKS, RDS
Orchestration: Kubernetes
```

---

## 개발 환경 준비

### 1. 필수 도구 설치

#### Windows 환경
```bash
# Git 설치
https://git-scm.com/download/win

# JDK 17 설치
https://adoptium.net/temurin/releases/

# Docker Desktop 설치
https://www.docker.com/products/docker-desktop/

# AWS CLI 설치
https://aws.amazon.com/cli/
```

#### Java 17 확인
```bash
java -version
# openjdk version "17.0.x" 확인
```

### 2. GitHub 리포지토리 생성
```bash
# 새 리포지토리 생성
git clone https://github.com/yourusername/course-registration.git
cd course-registration
```

### 3. 프로젝트 구조 생성
```
course-registration/
├── src/
│   ├── main/
│   │   ├── java/com/example/registrationweb/
│   │   └── resources/
│   └── test/
├── build.gradle
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci-cd.yml
└── k8s/
    ├── namespace.yaml
    ├── deployment.yaml
    ├── service.yaml
    └── configmap.yaml
```

---

## Spring Boot 애플리케이션 개발

### 1. build.gradle 설정
```gradle
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.1.2'
    id 'io.spring.dependency-management' version '1.1.0'
}

group = 'com.example'
version = '0.0.1-SNAPSHOT'
java.sourceCompatibility = JavaVersion.VERSION_17

repositories {
    mavenCentral()
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.boot:spring-boot-starter-mustache'
    implementation 'mysql:mysql-connector-java:8.0.33'
    runtimeOnly 'com.h2database:h2'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```

### 2. 메인 애플리케이션 클래스
```java
// src/main/java/com/example/registrationweb/RegistrationwebApplication.java
@SpringBootApplication
public class RegistrationwebApplication {
    public static void main(String[] args) {
        SpringApplication.run(RegistrationwebApplication.class, args);
    }
}
```

### 3. 엔티티 모델 개발

#### Student 엔티티
```java
@Entity
@Table(name = "students")
public class Student {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true)
    private String studentId;
    
    private String name;
    private String department;
    private String password;
    private Integer grade;
    
    // Getters, Setters, Constructors
}
```

#### Subject 엔티티
```java
@Entity
@Table(name = "subjects")
public class Subject {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String year;
    private String department;
    private String subjectName;
    private String subjectCode;
    private String courseType;
    private Integer credit;
    private String weekday;
    private String period;
    private String professor;
    private Integer capacity;
    
    // Getters, Setters, Constructors
}
```

#### Enrollment 엔티티
```java
@Entity
@Table(name = "enrollments")
public class Enrollment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "student_id")
    private Student student;
    
    @ManyToOne
    @JoinColumn(name = "subject_id")
    private Subject subject;
    
    // Getters, Setters, Constructors
}
```

### 4. Repository 계층
```java
// StudentRepository.java
@Repository
public interface StudentRepository extends JpaRepository<Student, Long> {
    Optional<Student> findByStudentId(String studentId);
    boolean existsByStudentId(String studentId);
}

// SubjectRepository.java
@Repository
public interface SubjectRepository extends JpaRepository<Subject, Long> {
    List<Subject> findByYearAndDepartment(String year, String department);
}

// EnrollmentRepository.java
@Repository
public interface EnrollmentRepository extends JpaRepository<Enrollment, Long> {
    List<Enrollment> findByStudentStudentId(String studentId);
    boolean existsByStudentIdAndSubjectId(Long studentId, Long subjectId);
}
```

### 5. Service 계층
```java
@Service
@Transactional
public class StudentService {
    private final StudentRepository studentRepository;
    
    public StudentService(StudentRepository studentRepository) {
        this.studentRepository = studentRepository;
    }
    
    public List<Student> getAllStudents() {
        return studentRepository.findAll();
    }
    
    public Student saveStudent(Student student) {
        return studentRepository.save(student);
    }
    
    // 기타 메서드들...
}
```

### 6. Controller 계층
```java
@Controller
public class LoginController {
    
    @GetMapping("/")
    public String home() {
        return "redirect:/login";
    }
    
    @GetMapping("/login")
    public String loginForm() {
        return "login";
    }
    
    @PostMapping("/login")
    public String login(@RequestParam String username, 
                       @RequestParam String password, 
                       HttpSession session) {
        // 로그인 로직
        session.setAttribute("user", username);
        return "redirect:/student/home";
    }
}
```

### 7. 데이터베이스 현황 서비스 (추가 기능)
```java
@Service
public class DatabaseStatusService {
    private final StudentRepository studentRepository;
    private final SubjectRepository subjectRepository;
    private final EnrollmentRepository enrollmentRepository;
    
    public Map<String, Object> getDatabaseStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("studentCount", studentRepository.count());
        status.put("subjectCount", subjectRepository.count());
        status.put("enrollmentCount", enrollmentRepository.count());
        status.put("connectionStatus", "Connected");
        status.put("databaseType", "MySQL");
        return status;
    }
}
```

### 8. 설정 파일

#### application.properties
```properties
# 기본 설정
spring.application.name=registrationweb
server.port=8087

# Mustache 설정
spring.mustache.prefix=classpath:/templates/
spring.mustache.suffix=.mustache

# H2 Database (로컬 개발용)
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driver-class-name=org.h2.Driver
spring.jpa.hibernate.ddl-auto=update
```

#### application-prod.properties (AWS 배포용)
```properties
# MySQL 설정
spring.datasource.url=jdbc:mysql://${DB_HOST:localhost}:${DB_PORT:3306}/${DB_NAME:registrationdb}
spring.datasource.username=${DB_USERNAME:root}
spring.datasource.password=${DB_PASSWORD:password}
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

# JPA 설정
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=false
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQLDialect

# SQL 초기화 비활성화 (중요!)
spring.sql.init.mode=${SPRING_SQL_INIT_MODE:always}
```

---

## Docker 컨테이너화

### 1. Dockerfile 작성
```dockerfile
# 멀티스테이지 빌드
FROM gradle:8.13-jdk17-alpine AS builder
WORKDIR /workspace

# 의존성 캐싱을 위한 단계별 복사
COPY build.gradle settings.gradle ./
COPY gradle/ gradle/
COPY gradlew ./
RUN chmod +x gradlew && ./gradlew dependencies --no-daemon

# 소스 코드 복사 및 빌드
COPY src/ src/
RUN ./gradlew clean bootJar --no-daemon

# 실행 단계
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# 빌드된 JAR 파일 복사
COPY --from=builder /workspace/build/libs/*.jar app.jar

# 애플리케이션 실행
EXPOSE 8087
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

### 2. .dockerignore 파일
```
.git
.gradle
build/
node_modules/
*.md
.gitignore
Dockerfile
docker-compose.yml
```

### 3. 로컬 테스트용 docker-compose.yml
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8087:8087"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_NAME=registrationdb
      - DB_USERNAME=root
      - DB_PASSWORD=password123
    depends_on:
      - mysql

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password123
      MYSQL_DATABASE: registrationdb
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

### 4. Docker 이미지 빌드 및 테스트
```bash
# 이미지 빌드
docker build -t course-registration .

# 로컬 실행 테스트
docker-compose up -d

# 로그 확인
docker-compose logs -f app

# 정리
docker-compose down
```

---

## AWS 인프라 구축

### 1. AWS CLI 설정
```bash
# AWS CLI 설치 확인
aws --version

# AWS 계정 설정
aws configure
# Access Key ID: [Your Access Key]
# Secret Access Key: [Your Secret Key]
# Default region: us-east-1
# Default output format: json
```

### 2. EC2 인스턴스 생성
```bash
# 키 페어 생성
aws ec2 create-key-pair --key-name course-registration-key \
  --query 'KeyMaterial' --output text > course-registration-key.pem

# 권한 설정 (Linux/Mac)
chmod 400 course-registration-key.pem

# 보안 그룹 생성
aws ec2 create-security-group \
  --group-name course-registration-sg \
  --description "Security group for course registration app"

# HTTP 포트 허용
aws ec2 authorize-security-group-ingress \
  --group-name course-registration-sg \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

# SSH 포트 허용
aws ec2 authorize-security-group-ingress \
  --group-name course-registration-sg \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

# EC2 인스턴스 생성
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t2.micro \
  --key-name course-registration-key \
  --security-groups course-registration-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=course-registration-server}]'
```

### 3. RDS MySQL 데이터베이스 생성
```bash
# DB 서브넷 그룹 생성
aws rds create-db-subnet-group \
  --db-subnet-group-name course-registration-subnet-group \
  --db-subnet-group-description "Subnet group for course registration DB" \
  --subnet-ids subnet-xxx subnet-yyy

# RDS 인스턴스 생성
aws rds create-db-instance \
  --db-instance-identifier course-registration-db \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password YourPassword123! \
  --allocated-storage 20 \
  --db-name registrationdb \
  --vpc-security-group-ids sg-xxx \
  --db-subnet-group-name course-registration-subnet-group \
  --publicly-accessible
```

### 4. EKS 클러스터 생성
```bash
# eksctl 설치 (Windows)
choco install eksctl

# EKS 클러스터 생성
eksctl create cluster \
  --name course-registration-eks \
  --region us-east-1 \
  --nodegroup-name workers \
  --node-type t3.small \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed

# kubectl 설정
aws eks update-kubeconfig --region us-east-1 --name course-registration-eks

# 클러스터 확인
kubectl get nodes
```

---

## CI/CD 파이프라인 구축

### 1. GitHub Secrets 설정
GitHub 리포지토리 Settings > Secrets and variables > Actions에서 다음 설정:

```
DOCKERHUB_USERNAME: your-dockerhub-username
DOCKERHUB_PASSWORD: your-dockerhub-password
EC2_SSH_KEY: [EC2 private key content]
EC2_HOSTNAME: your-ec2-public-ip
DB_HOST: your-rds-endpoint
DB_PORT: 3306
DB_NAME: registrationdb
DB_USERNAME: admin
DB_PASSWORD: YourPassword123!
```

### 2. GitHub Actions Workflow 작성
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        
    - name: Cache Gradle packages
      uses: actions/cache@v3
      with:
        path: |
          ~/.gradle/caches
          ~/.gradle/wrapper
        key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
        restore-keys: |
          ${{ runner.os }}-gradle-
          
    - name: Grant execute permission for gradlew
      run: chmod +x gradlew
      
    - name: Run tests
      run: ./gradlew test
      
    - name: Build application
      run: ./gradlew build -x test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
        
    - name: Cache Gradle packages
      uses: actions/cache@v3
      with:
        path: |
          ~/.gradle/caches
          ~/.gradle/wrapper
        key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
        restore-keys: |
          ${{ runner.os }}-gradle-
          
    - name: Grant execute permission for gradlew
      run: chmod +x gradlew
      
    - name: Build application
      run: ./gradlew build -x test
      
    - name: Login to DockerHub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_PASSWORD }}
        
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKERHUB_USERNAME }}/course-registration:latest
          ${{ secrets.DOCKERHUB_USERNAME }}/course-registration:${{ github.sha }}
        
    - name: Deploy to EC2
      env:
        PRIVATE_KEY: ${{ secrets.EC2_SSH_KEY }}
        HOSTNAME: ${{ secrets.EC2_HOSTNAME }}
        USER_NAME: ubuntu
        DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
      run: |
        echo "$PRIVATE_KEY" > private_key && chmod 600 private_key
        ssh -o StrictHostKeyChecking=no -i private_key ${USER_NAME}@${HOSTNAME} '
          # Install Docker if not exists
          if ! command -v docker &> /dev/null; then
            sudo apt update -y
            sudo apt install -y docker.io
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -a -G docker ubuntu
          fi
          
          # Stop and remove existing container
          sudo docker stop course-registration || true
          sudo docker rm course-registration || true
          
          # Pull and run new image
          sudo docker pull '$DOCKERHUB_USERNAME'/course-registration:latest
          sudo docker run -d --name course-registration -p 80:8087 \
            -e SPRING_PROFILES_ACTIVE=prod \
            -e SPRING_SQL_INIT_MODE=never \
            -e DB_HOST=${{ secrets.DB_HOST }} \
            -e DB_PORT=${{ secrets.DB_PORT }} \
            -e DB_NAME=${{ secrets.DB_NAME }} \
            -e DB_USERNAME=${{ secrets.DB_USERNAME }} \
            -e DB_PASSWORD=${{ secrets.DB_PASSWORD }} \
            -v /home/ubuntu/uploads:/app/uploads \
            '$DOCKERHUB_USERNAME'/course-registration:latest
        '
```

---

## EKS + ArgoCD 배포

### 1. Kubernetes 매니페스트 작성

#### k8s/namespace.yaml
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: course-registration
  labels:
    name: course-registration
```

#### k8s/configmap.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: course-registration-config
  namespace: course-registration
data:
  application.properties: |
    spring.mustache.prefix=classpath:/templates/
    spring.mustache.suffix=.mustache
    spring.mustache.cache=true
    server.address=0.0.0.0
    server.port=8087
    spring.application.name=registrationweb
    server.servlet.encoding.charset=UTF-8
    server.servlet.encoding.enabled=true
    server.servlet.encoding.force=true
    spring.mustache.charset=UTF-8
    spring.servlet.multipart.enabled=true
    spring.servlet.multipart.max-file-size=10MB
    spring.servlet.multipart.max-request-size=10MB
    file.upload.directory=uploads/syllabus
```

#### k8s/deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: course-registration
  namespace: course-registration
  labels:
    app: course-registration
spec:
  replicas: 2
  selector:
    matchLabels:
      app: course-registration
  template:
    metadata:
      labels:
        app: course-registration
    spec:
      containers:
      - name: course-registration
        image: procof/course-registration:latest
        ports:
        - containerPort: 8087
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
        - name: SPRING_SQL_INIT_MODE
          value: "never"
        - name: DB_HOST
          value: "your-rds-endpoint.rds.amazonaws.com"
        - name: DB_PORT
          value: "3306"
        - name: DB_NAME
          value: "registrationdb"
        - name: DB_USERNAME
          value: "admin"
        - name: DB_PASSWORD
          value: "YourPassword123!"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 8087
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 8087
          initialDelaySeconds: 30
          periodSeconds: 15
```

#### k8s/service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: course-registration-service
  namespace: course-registration
  labels:
    app: course-registration
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8087
    protocol: TCP
  selector:
    app: course-registration
```

### 2. ArgoCD 설치
```bash
# ArgoCD 네임스페이스 생성
kubectl create namespace argocd

# ArgoCD 설치
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# ArgoCD 서비스 포트 포워딩
kubectl port-forward svc/argocd-server -n argocd 8080:443

# ArgoCD 초기 비밀번호 확인
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### 3. ArgoCD 애플리케이션 설정
```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: course-registration
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/seokheounjo/Course_registration
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: course-registration
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

```bash
# ArgoCD 애플리케이션 배포
kubectl apply -f argocd-application.yaml
```

### 4. VPC 피어링 설정 (EKS-RDS 연결)
```bash
# EKS 클러스터 VPC ID 확인
aws eks describe-cluster --name course-registration-eks --query 'cluster.resourcesVpcConfig.vpcId'

# RDS VPC ID 확인
aws rds describe-db-instances --db-instance-identifier course-registration-db --query 'DBInstances[0].DBSubnetGroup.VpcId'

# VPC 피어링 연결 생성
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-eks-id \
  --peer-vpc-id vpc-rds-id

# 피어링 연결 수락
aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id pcx-xxx

# 라우팅 테이블 업데이트
# (각 VPC의 라우팅 테이블에 상대방 CIDR 블록 추가)
```

---

## 문제해결 및 디버깅

### 1. 일반적인 문제들

#### Docker 빌드 실패
```bash
# 문제: gradlew 권한 없음
# 해결: Dockerfile에서 권한 설정
RUN chmod +x gradlew

# 문제: 의존성 다운로드 실패
# 해결: 네트워크 확인 및 Gradle 캐시 정리
./gradlew clean build --refresh-dependencies
```

#### GitHub Actions 실패
```bash
# 문제: DockerHub 로그인 실패
# 해결: DOCKERHUB_PASSWORD 시크릿 확인

# 문제: EC2 SSH 연결 실패
# 해결: 키 파일 형식 및 사용자명 확인 (ubuntu vs ec2-user)
```

#### 데이터베이스 연결 문제
```bash
# 문제: MySQL 연결 실패
# 해결: RDS 보안 그룹 인바운드 규칙 확인

# 문제: 중복 키 에러
# 해결: SPRING_SQL_INIT_MODE=never 설정
```

#### VPC 네트워킹 문제
```bash
# 문제: EKS에서 RDS 접근 불가
# 해결: VPC 피어링 연결 및 라우팅 테이블 설정

# VPC 피어링 상태 확인
aws ec2 describe-vpc-peering-connections

# 라우팅 테이블 확인
aws ec2 describe-route-tables
```

### 2. 로그 확인 방법

#### Docker 컨테이너 로그
```bash
# EC2에서 컨테이너 로그 확인
docker logs course-registration

# 실시간 로그 추적
docker logs -f course-registration
```

#### Kubernetes 로그
```bash
# Pod 로그 확인
kubectl logs -n course-registration deployment/course-registration

# 실시간 로그 추적
kubectl logs -f -n course-registration deployment/course-registration
```

#### ArgoCD 동기화 상태
```bash
# ArgoCD CLI 설치
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64

# 애플리케이션 상태 확인
argocd app get course-registration

# 동기화 실행
argocd app sync course-registration
```

---

## 모니터링 및 운영

### 1. 애플리케이션 상태 모니터링

#### EC2 배포 상태 확인
```bash
# SSH 접속
ssh -i course-registration-key.pem ubuntu@your-ec2-ip

# 컨테이너 상태 확인
docker ps
docker stats course-registration

# 애플리케이션 로그 확인
docker logs course-registration
```

#### EKS 배포 상태 확인
```bash
# 클러스터 상태
kubectl get nodes

# 애플리케이션 상태
kubectl get all -n course-registration

# Pod 세부 정보
kubectl describe pod -n course-registration

# 서비스 확인
kubectl get svc -n course-registration
```

### 2. 데이터베이스 모니터링
```bash
# RDS 인스턴스 상태 확인
aws rds describe-db-instances --db-instance-identifier course-registration-db

# 연결 테스트
mysql -h your-rds-endpoint -u admin -p registrationdb
```

### 3. ArgoCD 대시보드
- URL: `https://localhost:8080`
- Username: `admin`
- Password: [kubectl로 확인한 초기 비밀번호]

### 4. 애플리케이션 접근
- **EC2**: `http://your-ec2-ip`
- **EKS**: LoadBalancer 외부 IP 확인 후 접근

### 5. 성능 최적화

#### 리소스 사용량 모니터링
```bash
# Kubernetes 리소스 사용량
kubectl top nodes
kubectl top pods -n course-registration

# Docker 리소스 사용량
docker stats
```

#### 스케일링
```bash
# 수평 스케일링
kubectl scale deployment course-registration --replicas=3 -n course-registration

# 오토스케일링 설정
kubectl autoscale deployment course-registration --cpu-percent=50 --min=1 --max=10 -n course-registration
```

---

## 💡 팁과 모범사례

### 1. 보안
- AWS IAM 역할 기반 접근 제어 사용
- 민감한 정보는 GitHub Secrets 또는 Kubernetes Secrets 사용
- 정기적인 보안 업데이트 수행

### 2. 성능
- Docker 이미지 멀티스테이지 빌드로 크기 최적화
- Kubernetes 리소스 제한 설정
- 데이터베이스 인덱스 최적화

### 3. 운영
- 정기적인 백업 수행
- 모니터링 알림 설정
- 롤백 계획 수립

### 4. 개발
- 브랜치 전략 수립 (GitFlow)
- 코드 리뷰 프로세스 도입
- 테스트 자동화 확대

---

## 🎯 다음 단계

1. **Prometheus + Grafana 모니터링 구축**
2. **ELK Stack 로그 관리 시스템 도입**
3. **Helm Chart 패키지 관리 적용**
4. **Terraform Infrastructure as Code 도입**
5. **마이크로서비스 아키텍처로 확장**

---

## 📞 지원 및 문의

- **GitHub**: https://github.com/seokheounjo/Course_registration
- **개발자**: 조석현
- **개발기간**: 2025년 8월 11일 ~ 15일

이 가이드를 따라하면 처음부터 끝까지 완전한 CI/CD 파이프라인을 구축할 수 있습니다. 각 단계에서 문제가 발생하면 문제해결 섹션을 참고하세요!