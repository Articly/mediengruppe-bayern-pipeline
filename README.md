# mgb-pipeline

## Build Docker image

```bash
docker build -t mgb-pipeline .
```

## Run Docker container

```bash
docker run --rm --env-file .env --network host mgb-pipeline
```

## Tag and push docker image

```bash
az acr login -n articly
```

```bash
docker tag mgb-pipeline:latest articly.azurecr.io/mgb/pipeline:v1
docker push articly.azurecr.io/mgb/pipeline:v1
```

## Deploy to Kubernetes

```bash
kubectl apply -f kubernetes/secrets/mgb-secrets.yaml
``

```bash
kubectl apply -f kubernetes/prod/pipeline-cronjob.yaml
``
