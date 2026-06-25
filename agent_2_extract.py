import json
import boto3 # type: ignore
import uuid

# Initialize clients targeting the Sydney region
bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-southeast-2')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BusinessChangeRequests')

def lambda_handler(event, context):
    raw_text = event.get('raw_text', '')
    classification = event.get('classification', 'Unknown')
    
    prompt = (
        f"System: You are an expert Data Extraction Agent. Read the following business request "
        f"and extract: 'user_name', 'app_name', and 'urgency' (High/Medium/Low). "
        f"Return the response ONLY as a single valid flat JSON object. Do not include markdown formatting or backticks.\n\n"
        f"Request: {raw_text}"
    )
    
    native_request = {
        "inferenceConfig": {
            "maxTokens": 150,
            "temperature": 0.0
        },
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ]
    }
    
    # Invoke Amazon Nova Micro
    response = bedrock.invoke_model(
        modelId='amazon.nova-micro-v1:0',
        body=json.dumps(native_request)
    )
    
    response_body = json.loads(response.get('body').read())
    extracted_text = response_body['output']['message']['content'][0]['text'].strip()
    
    # 1. Safely parse the LLM output into a dictionary
    try:
        # Strip common markdown wrappers if the model included them
        clean_text = extracted_text.replace("```json", "").replace("```", "").strip()
        extracted_data = json.loads(clean_text)
    except Exception as json_err:
        print(f"JSON Parsing failed: {json_err}")
        extracted_data = {"user_name": "Unknown", "app_name": "Unknown", "urgency": "Medium"}
        
    request_id = str(uuid.uuid4())[:8]
    
    # 2. Persist to DynamoDB (Kept outside try/except to expose errors if it fails)
    table.put_item(
        Item={
            'RequestID': request_id, 
            'RawText': raw_text,
            'Classification': classification,
            'ExtractedData': extracted_data
        }
    )
    
    return {
        "request_id": request_id,
        "raw_text": raw_text,
        "classification": classification,
        "extracted_data": extracted_data
    }