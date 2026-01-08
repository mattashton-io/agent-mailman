import os
import argparse
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
        # list_locations requires a request object or dict
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

def list_vertex_resources_in_region(project, location):
    """Lists resources in a specific region."""
    try:
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
        if "503" not in str(e): # Avoid spamming reauth errors if they occur
             print(f"  Error or not enabled in this region: {e}")
        else:
             print("  Service unavailable or reauth required in this region.")

def delete_vertex_resources_in_region(project, location):
    """Deletes resources in a specific region."""
    try:
        aiplatform.init(project=project, location=location)
        
        # Delete Endpoints (force=True undeploys models)
        endpoints = aiplatform.Endpoint.list()
        if endpoints:
            print(f"  Deleting {len(endpoints)} endpoints...")
            for endpoint in endpoints:
                print(f"    - Deleting endpoint: {endpoint.display_name} ({endpoint.resource_name})")
                try:
                    endpoint.delete(force=True)
                except Exception as del_e:
                    print(f"      Failed to delete endpoint: {del_e}")
        else:
            print("  No endpoints to delete.")

        # Delete Models
        models = aiplatform.Model.list()
        if models:
            print(f"  Deleting {len(models)} models...")
            for model in models:
                print(f"    - Deleting model: {model.display_name} ({model.resource_name})")
                try:
                    model.delete()
                except Exception as del_e:
                    print(f"      Failed to delete model: {del_e}")
        else:
            print("  No models to delete.")
    except Exception as e:
        print(f"  Error during deletion in this region: {e}")

def main():
    # Load environment variables (as per spec)
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="List or Delete Vertex AI resources.")
    parser.add_argument("--delete", action="store_true", help="Delete all models and endpoints found.")
    args = parser.parse_args()

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")

    if not project:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable is not set.")
        return

    print(f"Programmatically discovering Vertex AI regions for project: {project}...")
    regions = get_available_regions(project)
    
    if not regions:
        print("No regions found.")
        return

    print(f"Found {len(regions)} regions. {'DELETING' if args.delete else 'Scanning'} resources...\n")

    for location in regions:
        print(f"--- Region: {location} ---")
        if args.delete:
            delete_vertex_resources_in_region(project, location)
        else:
            list_vertex_resources_in_region(project, location)
        print("-" * 30 + "\n")

if __name__ == "__main__":
    main()
