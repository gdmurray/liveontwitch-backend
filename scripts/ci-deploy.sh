#! /bin/bash
set -e
COMMIT_SHA1=$CIRCLE_SHA1

export COMMIT_SHA1=$COMMIT_SHA1

# since the only way for envsubst to work on files is using input/output redirection,
#  it's not possible to do in-place substitution, so we need to save the output to another file
#  and overwrite the original with that one.
envsubst <./kube/django/deployment.yaml >./kube/django/deployment.yaml.out
mv ./kube/django/deployment.yaml.out ./kube/django/deployment.yaml

envsubst <./kube/django/job-migration.yaml >./kube/django/job-migration.yaml.out
mv ./kube/django/job-migration.yaml.out ./kube/django/job-migration.yaml

echo "$KUBERNETES_CLUSTER_CERTIFICATE" | base64 --decode > cert.crt

./kubectl \
  --kubeconfig=/dev/null \
  --server=$KUBERNETES_SERVER \
  --certificate-authority=cert.crt \
  --token=$KUBERNETES_TOKEN \
  apply -f ./kube/