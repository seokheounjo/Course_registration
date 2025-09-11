#!/bin/bash

echo "=== Minimal Deployment Script ==="

# Step 1: Install required packages
echo "Step 1: Installing required packages..."
sudo apt-get update > /dev/null 2>&1
sudo apt-get install -y openjdk-17-jdk mysql-client > /dev/null 2>&1

# Step 2: Verify installations
echo "Step 2: Verifying installations..."
java -version
mysql --version

# Step 3: Test RDS connection
echo "Step 3: Testing RDS connection..."
if mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USERNAME" -p"$DB_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; then
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USERNAME" -p"$DB_PASSWORD" -e "SELECT 1"
    echo "✅ RDS connection successful"
    
    # Step 4: Update RDS database schema and data
    echo "Step 4: Updating RDS database..."
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USERNAME" -p"$DB_PASSWORD" "$DB_NAME" < schema.sql 2>/dev/null || true
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USERNAME" -p"$DB_PASSWORD" "$DB_NAME" < data.sql 2>/dev/null || true
    
    # Step 5: Start application with RDS
    echo "Step 5: Starting application with RDS..."
    
    # Kill any existing Java processes
    pkill -f 'java.*app.jar' || true
    sleep 2
    
    # Start the application with proper Spring profiles and datasource configuration
    nohup java -Xmx512m -Xms256m -jar app.jar \
        --spring.profiles.active=prod \
        --spring.datasource.url="jdbc:mysql://${DB_HOST}:${DB_PORT}/${DB_NAME}?useSSL=false&allowPublicKeyRetrieval=true" \
        --spring.datasource.username="${DB_USERNAME}" \
        --spring.datasource.password="${DB_PASSWORD}" \
        --spring.jpa.hibernate.ddl-auto=validate \
        --spring.jpa.show-sql=false \
        --server.port=8087 > /tmp/app.log 2>&1 &
    
    # Get the PID of the java process
    APP_PID=$!
    echo "Application PID: $APP_PID"
    
    # Wait for application to start (give it more time)
    echo "Waiting for application to start..."
    for i in {1..30}; do
        sleep 2
        
        # Check if process is still running
        if ! ps -p $APP_PID > /dev/null; then
            echo ""
            echo "❌ Application process died unexpectedly"
            echo "=== Application log ==="
            cat /tmp/app.log
            exit 1
        fi
        
        # Check if application is responding
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8087 | grep -q "200\|302"; then
            echo ""
            echo "✅ Application started successfully"
            exit 0
        fi
        echo -n "."
    done
    
    echo ""
    echo "❌ Application failed to start after 60 seconds"
    echo "=== Last 100 lines of application log ==="
    tail -n 100 /tmp/app.log
    exit 1
else
    echo "❌ RDS connection failed"
    echo "Starting with H2 fallback..."
    
    # Kill any existing Java processes
    pkill -f 'java.*app.jar' || true
    sleep 2
    
    # Start with H2 database
    nohup java -jar app.jar \
        --server.port=8087 \
        --spring.datasource.url="jdbc:h2:mem:testdb" \
        --spring.jpa.hibernate.ddl-auto=create-drop > /tmp/app.log 2>&1 &
    
    echo "Waiting for application to start with H2..."
    for i in {1..30}; do
        sleep 2
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8087 | grep -q "200\|302"; then
            echo "✅ Application started with H2"
            exit 0
        fi
        echo -n "."
    done
    
    echo ""
    echo "❌ Application failed to start with H2"
    echo "=== Last 100 lines of application log ==="
    tail -n 100 /tmp/app.log
    exit 1
fi