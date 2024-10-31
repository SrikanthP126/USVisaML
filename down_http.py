import azure.functions as func
import azure.durable_functions as df
import os
from logging import INFO, getLogger
from azure.monitor.opentelemetry import configure_azure_monitor

# Set up monitoring and logging
configure_azure_monitor()
logger = getLogger(__name__)
logger.setLevel(INFO)

async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    function_name = req.route_params.get('functionName')
    
    try:
        # Explicitly parse JSON from the request body
        req_body = req.get_json()
        action = req_body.get("action")
        filepath = req_body.get("filepath")
        
        # Validation
        if action not in ["download", "list"]:
            logger.error("Invalid action provided")
            return func.HttpResponse("Invalid action provided. Must be 'download' or 'list'.", status_code=400)

        if action == "download" and not filepath:
            logger.error("Filepath not provided for download action")
            return func.HttpResponse("Filepath not provided for download action", status_code=400)

        logger.info(f"Starting orchestration with action={action}, filepath={filepath}")
        
        # Start orchestration with the provided action and filepath
        client = df.DurableOrchestrationClient(starter)
        instance_id = await client.start_new(function_name, None, {"action": action, "filepath": filepath})
        response = client.create_check_status_response(req, instance_id)
        
        return response

    except ValueError:
        return func.HttpResponse("Invalid JSON in request body", status_code=400)
