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
    # Retrieve function name from route parameters
    function_name = req.route_params.get('functionName')
    # Get action and filepath from the request
    action = req.params.get('action')
    filepath = req.params.get('filepath')

    # Validate action and filepath based on requested action
    if action not in ["download", "list"]:
        logger.error("Invalid action provided")
        return func.HttpResponse("Invalid action provided. Must be 'download' or 'list'.", status_code=400)

    if action == "download" and not filepath:
        logger.error("Filepath not provided for download action")
        return func.HttpResponse("Filepath not provided for download action", status_code=400)

    # Log start of orchestration
    logger.info(f"Starting orchestration with action={action}, filepath={filepath}")

    # Start the orchestration
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new(function_name, None, {"action": action, "filepath": filepath})
    response = client.create_check_status_response(req, instance_id)
    
    # Return orchestration status response
    return response
