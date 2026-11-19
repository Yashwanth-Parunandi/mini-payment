# Setup and Prerequisites

- Java JDK 21+
- Docker Engine 24+ & Docker Compose
- Node.js 20+

## Local Execution:
1. `docker-compose up -d postgres redis`
2. `cd backend && ./mvnw spring-boot:run`
3. `cd frontend && npm start`
