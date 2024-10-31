import azure.durable_functions as df
from logging import INFO, getLogger
from azure.monitor.opentelemetry import configure_azure_monitor

# Set up monitoring and logging
configure_azure_monitor()
logger = getLogger(__name__)
logger.setLevel(INFO)

def BlobOrchestrator(context: df.DurableOrchestrationContext):
    try:
        # Retrieve input data passed from the Http Starter
        input_data = context.get_input()
        logger.info(f"Received input data: {input_data}")

        # Extract action and filepath from input
        action = input_data.get("action")
        filepath = input_data.get("filepath", None)

        # Call the appropriate activity based on action
        if action == "list":
            logger.info("Starting blob listing activity")
            result = yield context.call_activity("BlobListingActivity", {})
        
        elif action == "download":
            if not filepath:
                raise ValueError("Filepath must be provided for download action")
            
            logger.info(f"Starting blob download activity for filepath: {filepath}")
            result = yield context.call_activity("BlobDownloadActivity", {"filepath": filepath})
        
        else:
            raise ValueError(f"Invalid action provided: {action}")

    except Exception as e:
        logger.error(f"Error in orchestrator: {str(e)}")
        result = {"status": "failed", "message": str(e)}

    return result

# Register the orchestrator function
main = df.Orchestrator.create(BlobOrchestrator)
