import json
import boto3

# Getting bucket ready
s3 = boto3.client('s3')
s3_name = 'smartsafe-logs'

def lambda_handler(event, context):
    try:
        # Extracting data from input
        time = event.get('time')
        status = event.get('status')
        cam1 = event.get('cam1')
        cam2 = event.get('cam2')
        last_opened = event.get('last opened')

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid input: ' + str(e))
        }
    
    # Calculating the runtime
    if(last_opened != 0):
        duration = time - last_opened
    else:
        duration = 0
    
    # Preparing the processed result
    processed_result = {
        "time": time,
        "status": status,
        "cam1": cam1,
        "cam2": cam2,
        "duration": duration,
    }
    
    # Saving raw data to S3
    s3.put_object(
        Bucket=s3_name,
        Key=f"raw_data/smartsafe_raw_{time}.json",
        Body=json.dumps(event)
    )
    
    # Saving processed result to S3
    s3.put_object(
        Bucket=s3_name,
        Key=f"processed_data/smartsafe_processed_{time}.json",
        Body=json.dumps(processed_result) 
    )
    
    return {
        'statusCode': 200,
        "body": json.dumps(f'Data processed and saved with duration: {duration}')
    }