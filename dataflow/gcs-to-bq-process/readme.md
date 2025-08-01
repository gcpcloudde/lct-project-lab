"This is for gcs to bigquery ingestion pipeline"



Build Command:
-----------
gcloud dataflow flex-template build gs://dataflow-flex-template-ex-demo/getting_started-py.json  --image-gcr-path "us-central1-docker.pkg.dev/lhn-dev-project/dataflow-flex-templates/getting-started-python:latest"  --sdk-language "PYTHON"  --flex-template-base-image "PYTHON3"  --metadata-file "metadata.json"  --py-path "."  --env "FLEX_TEMPLATE_PYTHON_PY_FILE=getting_started.py"  --env "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt"


Run command:
-------------
gcloud dataflow flex-template run "getting-started-`date +%Y%m%d-%H%M%S`" \
 --template-file-gcs-location "gs://BUCKET_NAME/getting_started-py.json" \
 --parameters output="gs://BUCKET_NAME/output-" \
 --additional-user-labels "LABELS" \
 --region "REGION"
 
UserInterface:
---------------

PowerShell:
------------
gcloud dataflow flex-template build "gs://dataflow-flex-template-ex-demo/gcstobqload.json" `
  --image-gcr-path "us-central1-docker.pkg.dev/lhn-dev-project/dataflow-flex-templates/gcstobqload-python:latest" `
  --sdk-language "PYTHON" `
  --flex-template-base-image "PYTHON3" `
  --metadata-file "metadata.json" `
  --py-path "." `
  --env "FLEX_TEMPLATE_PYTHON_PY_FILE=main.py" `
  --env "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt"
