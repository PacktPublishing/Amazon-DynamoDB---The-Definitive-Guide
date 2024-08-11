import random
import time


def lambda_handler(event, context):
    """
    AWS Lambda function that generates a shuffled list of numbers from 0 to 99 and assigns a unique run ID.

    Parameters:
        event (dict): The event triggering the Lambda function. Not used in this implementation.
        context (object): The context in which the Lambda function is invoked. Not used in this implementation.

    Returns:
        dict: A dictionary containing:
              - "numbers": A list of numbers from 0 to 99, shuffled in random order.
              - "runId": A unique identifier for this run, based on the current time in seconds since the epoch.
    """
    # Generate a list of numbers from 0 to 99
    numbers = list(range(0, 100))
    
    # Shuffle the list to randomize the order
    random.shuffle(numbers)
    
    # Generate a unique run ID based on the current time
    run_id = time.time()
    
    # Return the shuffled numbers and run ID
    return {
        "numbers": numbers,
        "runId": run_id
    }
