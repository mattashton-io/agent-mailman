import vertexai
from vertexai import model_garden

vertexai.init(project="pytutoring-dev", location="us-west1")

model = model_garden.OpenModel("google/codegemma@codegemma-7b")
endpoint = model.deploy(
  accept_eula=True,
  machine_type="ct5lp-hightpu-4t",
  serving_container_image_uri="us-docker.pkg.dev/vertex-ai-restricted/vertex-vision-model-garden-dockers/hex-llm-serve:20241210_2323_RC00",
  endpoint_display_name="google_codegemma-7b-mg-one-click-deploy",
  model_display_name="google_codegemma-7b-1767825323298",
  use_dedicated_endpoint=True,
)