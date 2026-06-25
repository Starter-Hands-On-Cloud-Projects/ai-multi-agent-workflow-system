import json
import boto3 # type: ignore

bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-southeast-2')

def lambda_handler(event, context):
    extracted_data = event.get('extracted_data', {})
    request_id = event.get('request_id')
    classification = event.get('classification')
    
    prompt = (
        f"System: You are an elite Customer Success AI Agent. Write a highly professional, reassuring, "
        f"and polite email to {extracted_data.get('user_name', 'Valued Customer')} acknowledging their request. "
        f"Mention that their request regarding '{extracted_data.get('app_name')}' has been officially cataloged "
        f"as a '{classification}' under tracking code Reference #{request_id} and routed to engineering.\n\n"
        f"Keep the response strictly limited to the finalized email text."
    )
    
    native_request = {
        "inferenceConfig": {
            "maxTokens": 400,
            "temperature": 0.5
        },
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ]
    }
    
    response = bedrock.invoke_model(
        modelId='amazon.nova-micro-v1:0',
        body=json.dumps(native_request)
    )
    
    response_body = json.loads(response.get('body').read())
    email_response = response_body['output']['message']['content'][0]['text'].strip()
    
    event['automated_email_response'] = email_response
    return event
