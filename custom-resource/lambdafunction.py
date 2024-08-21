import boto3, os
import json
import cfnresponse

def lambda_handler(event, context):
    
    print(event)
    
    try:
        s3 = boto3.client('s3')

        bucket_name = os.environ.get('BUCKET_NAME', event['ResourceProperties']['BucketName'])

        file_name = 'greetings.txt'
        file_content = 'World of Lambda!'

        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
        responseData = {}
        responseData['Data'] = 'File uploaded successfully'
        cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, "CustomResourcePhysicalID")
    
    except Exception as e:
         
         responseData = {}
         responseData['Data'] = str(e)
         cfnresponse.send(event, context, cfnresponse.FAILED, responseData, "CustomResourcePhysicalID")



# import boto3, os
# import json
# import cfnresponse
# from datetime import datetime

# s3_client = boto3.client('s3')

# def lambda_handler(event, context):
#     responseData = {}

#     try: 
#         bucket_name = event['ResourceProperties']['BucketName']
#         file_content = "Hello from Lambda!"
#         file_name = "lambda_message.txt"

# s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
#         responseData['Data'] = "Hello, World!"

#         cfnresponse.send(event, context, cfnresponse.SUCCESS, responseData, "CustomResourcePhysicalID")

#     except Exception as e:
#         print(f"Error: {str(e)}")
#         responseData['Data'] = "Error"
        
#         cfnresponse.send(event, context, cfnresponse.FAILED, responseData, "CustomResourcePhysicalID")











