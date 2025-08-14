#!/bin/bash

# AWS 배포 스크립트
# 사용법: ./aws-deploy.sh

set -e

echo "=== Course Registration AWS Deployment Script ==="

# 변수 설정
REGION="ap-northeast-2"
ECR_REPO_NAME="course-registration"
EC2_KEY_NAME="calender"
SECURITY_GROUP_NAME="course-registration-sg"
RDS_INSTANCE_ID="course-registration-db"

# 1. DockerHub 설정 확인 (ECR 대신 DockerHub 사용)
echo "1. Using DockerHub instead of ECR..."
echo "Make sure your DockerHub repository is created: [username]/course-registration"

# 2. Security Group 생성
echo "2. Creating Security Group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
  --group-name $SECURITY_GROUP_NAME \
  --description "Security group for Course Registration app" \
  --region $REGION \
  --query 'GroupId' --output text 2>/dev/null || \
  aws ec2 describe-security-groups \
  --group-names $SECURITY_GROUP_NAME \
  --region $REGION \
  --query 'SecurityGroups[0].GroupId' --output text)

echo "Security Group ID: $SECURITY_GROUP_ID"

# Security Group Rules 추가
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --region $REGION || echo "SSH rule already exists"

aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region $REGION || echo "HTTP rule already exists"

aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 3306 \
  --source-group $SECURITY_GROUP_ID \
  --region $REGION || echo "MySQL rule already exists"

# 3. RDS 서브넷 그룹 생성
echo "3. Creating RDS subnet group..."
aws rds create-db-subnet-group \
  --db-subnet-group-name course-registration-subnet-group \
  --db-subnet-group-description "Subnet group for Course Registration RDS" \
  --subnet-ids $(aws ec2 describe-subnets --region $REGION --query 'Subnets[0:2].SubnetId' --output text | tr '\t' ' ') \
  --region $REGION || echo "DB subnet group already exists"

# 4. RDS 인스턴스 생성 (MySQL 8.0, Free Tier)
echo "4. Creating RDS instance..."
aws rds create-db-instance \
  --db-instance-identifier $RDS_INSTANCE_ID \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --engine-version 8.0.35 \
  --master-username admin \
  --master-user-password $(openssl rand -base64 12) \
  --allocated-storage 20 \
  --db-name registrationdb \
  --vpc-security-group-ids $SECURITY_GROUP_ID \
  --db-subnet-group-name course-registration-subnet-group \
  --no-multi-az \
  --no-publicly-accessible \
  --storage-type gp2 \
  --region $REGION || echo "RDS instance already exists"

echo "Waiting for RDS instance to be available..."
aws rds wait db-instance-available --db-instance-identifier $RDS_INSTANCE_ID --region $REGION

# RDS 엔드포인트 가져오기
RDS_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier $RDS_INSTANCE_ID \
  --region $REGION \
  --query 'DBInstances[0].Endpoint.Address' --output text)

echo "RDS Endpoint: $RDS_ENDPOINT"

# 5. EC2 키 페어 확인 (calender 키 사용)
echo "5. Using existing EC2 Key Pair: $EC2_KEY_NAME"

# 6. EC2 인스턴스 생성 (t2.micro, Free Tier)
echo "6. Creating EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id ami-0c76973fbe0ee100c \
  --count 1 \
  --instance-type t2.micro \
  --key-name $EC2_KEY_NAME \
  --security-group-ids $SECURITY_GROUP_ID \
  --region $REGION \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=course-registration-server}]' \
  --query 'Instances[0].InstanceId' --output text)

echo "EC2 Instance ID: $INSTANCE_ID"

echo "Waiting for EC2 instance to be running..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# EC2 퍼블릭 IP 가져오기
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --region $REGION \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "EC2 Public IP: $PUBLIC_IP"

# 7. GitHub Secrets를 위한 정보 출력
echo ""
echo "=== GitHub Secrets Configuration ==="
echo "Add these secrets to your GitHub repository:"
echo "DOCKERHUB_USERNAME: [Your DockerHub username]"
echo "DOCKERHUB_PASSWORD: [Your DockerHub password or access token]"
echo "EC2_SSH_KEY: [Contents of ${EC2_KEY_NAME}.pem file]"
echo "EC2_HOSTNAME: $PUBLIC_IP"
echo "DB_HOST: $RDS_ENDPOINT"
echo "DB_PORT: 3306"
echo "DB_NAME: registrationdb"
echo "DB_USERNAME: admin"
echo "DB_PASSWORD: [The password generated above - check RDS console]"

echo ""
echo "=== Deployment Complete ==="
echo "Your application will be available at: http://$PUBLIC_IP"
echo "Don't forget to:"
echo "1. Add the GitHub secrets listed above"
echo "2. Push your code to trigger the CI/CD pipeline"
echo "3. Check RDS console for the database password"