FROM openjdk:17-jdk-slim

WORKDIR /app

# Copy gradle files
COPY build.gradle settings.gradle gradlew ./
COPY gradle/ gradle/

# Download dependencies
RUN chmod +x gradlew && ./gradlew dependencies --no-daemon

# Copy source code
COPY src/ src/

# Build application
RUN ./gradlew build -x test --no-daemon

# Create uploads directory
RUN mkdir -p uploads/syllabus

# Expose port
EXPOSE 8087

# Run application
CMD ["java", "-jar", "build/libs/registrationweb-0.0.1-SNAPSHOT.jar"]