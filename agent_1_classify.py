import json
import boto3 # type: ignore

bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-southeast-2')

def lambda_handler(event, context):
    raw_request = event.get('raw_text', '')
    
    prompt = f"System: You are an AI Triage Agent. Classify the following business change request into exactly one of these categories: Bug, Feature Request, or Billing Issue. Return ONLY the category name.\n\nUser request: {raw_request}"
    
    # Corrected schema format specifically matching Amazon Nova parameters
    native_request = {
        "inferenceConfig": {
            "maxTokens": 10,
            "temperature": 0.0
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
    classification = response_body['output']['message']['content'][0]['text'].strip()
    
    return {
        "raw_text": raw_request,
        "classification": classification
    }