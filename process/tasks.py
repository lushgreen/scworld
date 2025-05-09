# api/tasks.py
import time
import logging

from celery import shared_task

logger = logging.getLogger(__name__) # Get a logger instance

@shared_task(bind=True) # bind=True allows access to task instance (self)
def process_data(self, email, message):
    # Simulate a time-consuming task like sending an email or processing data.
    task_id = self.request.id
    logger.info(f"[Task ID: {task_id}] Starting processing for email: {email}")

    try:
        # Simulate work (e.g., API call, database operation, email sending)
        # Update task state for better progress tracking (optional)
        self.update_state(state='PROCESSING', meta={'progress': 50})
        time.sleep(10) # Simulate 10 seconds of work

        # Simulate success
        result_message = f"Successfully processed message for {email}."
        logger.info(f"[Task ID: {task_id}] {result_message}")

        # The return value of the task is stored in the result backend (Redis)
        return {'status': 'completed', 'email': email, 'info': result_message}

    except Exception as e:
        # Log the error
        logger.error(f"[Task ID: {task_id}] Error processing task for {email}: {e}", exc_info=True)

        # Update state to FAILURE and store exception info
        # self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})

        # You might want to raise the exception again if you want Celery's default
        # failure handling (e.g., retries defined elsewhere), or handle it fully here.
        # For simplicity, we'll just return an error status.
        # Note: If you raise an exception, it will automatically set the state to FAILURE.
        # raise e # Uncomment this if you want Celery's default failure handling

        # Returning a dictionary even on failure can be useful for the status endpoint
        return {'status': 'failed', 'email': email, 'info': f"Error: {str(e)}"}



#@shared_task
#def process_message(email, message):
    # Simulate processing
#    print(f'Processing for {email}: {message}')

    # You can expand this to send emails, save to DB, etc.

#@shared_task
#def process_data_task(data):
    # Background task to process the received data.
#    email = data.get('email')
#    message = data.get('message')
#    print(f'Processing data for email: {email}')
#    print(f'Message received: {message}')
#    time.sleep(15) # Simulate some background processing
#    print(f'Finished processing for: {email}')
#    return f'Processed email: {email}, message: {message}'


