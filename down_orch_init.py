# Import necessary modules
import azure.durable_functions as df
from logging import INFO, getLogger
from azure.monitor.opentelemetry import configure_azure_monitor
from datetime import timedelta
from azure.durable_functions.models.RetryOptions import RetryOptions

# Set up logging and monitoring
configure_azure_monitor()
logger = getLogger(__name__)
logger.setLevel(INFO)

# Define the orchestrator function
def BlobOrchestrator(context: df.DurableOrchestrationContext):
    try:
        # Get input data
        input_data = context.get_input()
        action = input_data.get("action")
        filepath = input_data.get("filepath", None)

        # Define retry options
        retry_options = RetryOptions(
            first_retry_interval_in_milliseconds=10000,  # 10 seconds
            max_number_of_attempts=3
        )

        # Invoke activities based on the action parameter
        if action == "list":
            logger.info("Starting blob listing activity")
            result = yield context.call_activity_with_retry(
                "download_azure_to_onprem_list", retry_options, {"action": "list"}
            )
        
        elif action == "download":
            if not filepath:
                raise ValueError("Filepath must be provided for download action")
            
            logger.info(f"Starting blob download activity for filepath: {filepath}")
            result = yield context.call_activity_with_retry(
                "download_azure_to_onprem_activity", retry_options, {"action": "download", "filepath": filepath}
            )

        else:
            raise ValueError(f"Invalid action provided: {action}")

        # Log and return the result of the activity
        logger.info(f"Activity completed successfully with result: {result}")
        return {"status": "success", "result": result}

    except Exception as e:
        # Log the error and return a failed status
        logger.error(f"Error in orchestrator: {str(e)}")
        return {"status": "failed", "message": str(e)}

# Register the orchestrator function
main = df.Orchestrator.create(BlobOrchestrator)
