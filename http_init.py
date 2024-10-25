import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

# Configure logging to Log Analytics or Application Insights
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=YOUR_INSTRUMENTATION_KEY"))

async def main(req: func.HttpRequest, starter: str):
    function_name = req.route_params.get('functionName')
    filepath = req.params.get('filepath')

    if not filepath:
        logger.error("Filepath not provided")
        return func.HttpResponse("Filepath not provided", status_code=400)

    blob_name = os.path.basename(filepath)
    logger.info(f"Starting orchestration for blob_name={blob_name}, filepath={filepath}")

    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new(function_name, None, {"blob_name": blob_name, "filepath": filepath})
    response = client.create_check_status_response(req, instance_id)

    logger.info(f"Orchestration started with instance_id: {instance_id}")
    return response
