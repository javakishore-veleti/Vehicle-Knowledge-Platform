# Multi-stage build for any VKP Spring Boot (multi-module Maven) service.
# Build context = the service root (e.g. Middleware/indexing-service). The bootable fat jar is
# always api/target/<domain>-service.jar (see CLAUDE.md). The shared libraries
# (vkp-session-security, vkp-jwt-rbac) are installed into the local Maven repo first.
#
#   docker build -f Infra/docker/java-service.Dockerfile \
#     --build-arg SERVICE=indexing-service --build-arg JAR=indexing-service.jar \
#     -t vkp/indexing-service:0.1.0 Middleware
#
# Note: context is Middleware/ so the build can also `mvn install` the shared libs.
ARG SERVICE
ARG JAR

FROM maven:3.9-eclipse-temurin-21 AS build
ARG SERVICE
WORKDIR /workspace
# Install the shared libraries first (consumed by every service).
COPY vkp-session-security/ vkp-session-security/
COPY vkp-jwt-rbac/ vkp-jwt-rbac/
RUN mvn -q -B -f vkp-session-security/pom.xml -DskipTests install \
 && mvn -q -B -f vkp-jwt-rbac/pom.xml -DskipTests install
# Build the service.
COPY ${SERVICE}/ ${SERVICE}/
RUN mvn -q -B -f ${SERVICE}/pom.xml -DskipTests package

FROM eclipse-temurin:21-jre AS runtime
ARG SERVICE
ARG JAR
WORKDIR /app
RUN useradd -r -u 1001 vkp
COPY --from=build /workspace/${SERVICE}/api/target/${JAR} /app/app.jar
USER 1001
EXPOSE 8080
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "/app/app.jar"]
