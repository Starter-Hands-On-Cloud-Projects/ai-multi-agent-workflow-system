import json
import boto3 # type: ignore

bedrock = boto3.client(service_name='bedrock-runtime', region_name='ap-southeast-2')

def lambda_handler(event, context):
    classification = event.get('classification')
    extracted_data = event.get('extracted_data', {})
    raw_text = event.get('raw_text')
    
    prompt = (
        f"System: You are a technical Jira Product Manager Agent. Build a structured Jira ticket description "
        f"using markdown based on the context below. Include sections for 'Summary', 'Category', 'Urgency', "
        f"and 'Steps to Reproduce / Details'.\n\n"
        f"Context Details:\n"
        f"- Target Application: {extracted_data.get('app_name')}\n"
        f"- Ticket Type: {classification}\n"
        f"- Priority Tier: {extracted_data.get('urgency')}\n"
        f"- Original Report: {raw_text}"
    )
    
    native_request = {
        "inferenceConfig": {
            "maxTokens": 500,
            "temperature": 0.3
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
    jira_spec = response_body['output']['message']['content'][0]['text'].strip()
    
    event['jira_ticket_spec'] = jira_spec
    return event
