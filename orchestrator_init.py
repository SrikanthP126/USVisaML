import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

# Configure logging to Log Analytics
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=YOUR_INSTRUMENTATION_KEY"))

def PostOIMOrchestrator(context: df.DurableOrchestrationContext):
    input_data = context.get_input()

    if input_data is None:
        logger.error("No input data received in Orchestrator")
        raise ValueError("Input data is None")

    blob_name = input_data.get("blob_name")
    filepath = input_data.get("filepath")

    if not blob_name or not filepath:
        logger.error(f"Invalid input: blob_name={blob_name}, filepath={filepath}")
        raise ValueError("Blob name or filepath is missing")

    logger.info(f"Starting activity for blob_name: {blob_name} from filepath: {filepath}")

    result = yield context.call_activity("OnpremtoAzure_Test_Activity", {"blob_name": blob_name, "filepath": filepath})

    logger.info(f"Activity result: {result}")
    return result
