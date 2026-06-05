# Multi-stage build for any VKP Spring Boot (multi-module Maven) service. Build context =
# Middleware/ so the build can install the shared libs (vkp-session-security, vkp-jwt-rbac) first.
#
# SERVICE  = the service directory to `mvn package` (builds its whole reactor).
# JAR_PATH = the fat jar path relative to Middleware/ (api/target/<svc>.jar for normal services;
#            the wfs-java executor is a sub-module at indexing-service/wfs-java/target/...).
#
#   docker build -f Infra/docker/java-service.Dockerfile \
#     --build-arg SERVICE=indexing-service \
#     --build-arg JAR_PATH=indexing-service/api/target/indexing-service.jar \
#     -t vkp/indexing-service:0.1.0 Middleware
ARG SERVICE
ARG JAR_PATH

FROM maven:3.9-eclipse-temurin-21 AS build
ARG SERVICE
WORKDIR /workspace
# Install the shared libraries first (consumed by every service).
COPY vkp-session-security/ vkp-session-security/
COPY vkp-jwt-rbac/ vkp-jwt-rbac/
RUN mvn -q -B -f vkp-session-security/pom.xml -DskipTests install \
 && mvn -q -B -f vkp-jwt-rbac/pom.xml -DskipTests install
# Build the service (its reactor includes sub-modules like wfs-java).
COPY ${SERVICE}/ ${SERVICE}/
RUN mvn -q -B -f ${SERVICE}/pom.xml -DskipTests package

FROM eclipse-temurin:21-jre AS runtime
ARG JAR_PATH
WORKDIR /app
RUN useradd -r -u 1001 vkp
COPY --from=build /workspace/${JAR_PATH} /app/app.jar
USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "/app/app.jar"]
