import os
from google.cloud import aiplatform
from google.cloud import aiplatform_v1
from dotenv import load_dotenv

def get_available_regions(project):
    """Programmatically lists all regions where Vertex AI is available for the project."""
    try:
        from google.cloud import aiplatform
        # Using the gapic client which often includes the list_locations mixin
        client = aiplatform.gapic.EndpointServiceClient()
        parent = f"projects/{project}"
        
        regions = []
        # list_locations returns a ListLocationsResponse object
        response = client.list_locations(request={"name": parent})
        for location in response.locations:
            regions.append(location.location_id)
        
        if not regions:
            # Fallback if list_locations returns nothing
            return ["us-central1"]
            
        regions.sort()
        return regions
    except Exception as e:
        print(f"Error fetching regions programmatically: {e}")
        # Fallback to us-central1 if discovery fails
        return ["us-central1"]

def list_vertex_resources():
    """Lists deployed models and endpoints in Vertex AI across all available regions."""
    # Load environment variables (as per spec)
    load_dotenv()
    
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")

    if not project:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable is not set.")
        return

    print(f"Programmatically discovering Vertex AI regions for project: {project}...")
    regions = get_available_regions(project)
    
    if not regions:
        print("No regions found.")
        return

    print(f"Found {len(regions)} regions. Scanning resources...\n")

    for location in regions:
        print(f"--- Region: {location} ---")
        try:
            # Initialize for the specific region
            # (Note: we use the v1 sdk for listing regions, but can use high-level sdk for resources)
            aiplatform.init(project=project, location=location)

            # List Models
            models = aiplatform.Model.list()
            if models:
                print(f"  [Models]")
                for model in models:
                    print(f"    - Name: {model.display_name}")
                    print(f"      ID: {model.resource_name}")
            else:
                print("  No models found.")

            # List Endpoints
            endpoints = aiplatform.Endpoint.list()
            if endpoints:
                print(f"  [Endpoints]")
                for endpoint in endpoints:
                    print(f"    - Name: {endpoint.display_name}")
                    print(f"      ID: {endpoint.resource_name}")
            else:
                print("  No endpoints found.")
        except Exception as e:
            # Some regions might not have the API enabled or have other restrictions
            print(f"  Error or not enabled in this region: {e}")
        
        print("-" * 30 + "\n")

if __name__ == "__main__":
    list_vertex_resources()
