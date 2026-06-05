# Build for a SINGLE-module Spring Boot service (e.g. ContextEnggFramework's context-admin-service),
# whose fat jar is target/<name>.jar (not api/target). Build context = the service root.
#
#   docker build -f Infra/docker/java-single.Dockerfile \
#     -t vkp/context-admin-service:0.1.0 ContextEnggFramework/Middleware/context-admin-service
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn -q -B -DskipTests dependency:go-offline || true
COPY src ./src
RUN mvn -q -B -DskipTests package

FROM eclipse-temurin:21-jre AS runtime
WORKDIR /app
RUN useradd -r -u 1001 vkp
COPY --from=build /app/target/*.jar /app/app.jar
USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "/app/app.jar"]
