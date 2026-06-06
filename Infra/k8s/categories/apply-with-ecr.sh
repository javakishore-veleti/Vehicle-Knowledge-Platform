#!/usr/bin/env bash
# Render a category kustomization and apply OR delete it, rewriting every vkp/* image reference to
# the ECR registry + tag on apply. Public images (postgres/mongo) pass through untouched. Used by the
# AWS_005..009 Setup/Destroy workflows.
#
#   apply-with-ecr.sh <category-dir> <ecr-registry> <image-tag> [apply|delete]
#
# Notes:
#  - LoadRestrictionsNone lets the category kustomizations reference ../../base and ../../platform.
#  - The indexing-wfs repo name differs from its image name, so it is rewritten first (before the
#    generic vkp/<name> -> <reg>/vkp-<name> rule).
#  - On delete the image rewrite is skipped (delete matches by kind/name/namespace, not image).
set -euo pipefail
DIR="$1"; REG="${2:-}"; TAG="${3:-}"; ACTION="${4:-apply}"

render() { kubectl kustomize --load-restrictor=LoadRestrictionsNone "$DIR"; }

if [[ "$ACTION" == "delete" ]]; then
  render | kubectl delete --ignore-not-found=true -f -
else
  render \
    | sed -E "s#image: vkp/indexing-service-wfs-java:[^[:space:]]+#image: ${REG}/vkp-indexing-wfs:${TAG}#g" \
    | sed -E "s#image: vkp/([a-z0-9-]+):[^[:space:]]+#image: ${REG}/vkp-\1:${TAG}#g" \
    | kubectl apply -f -
fi
