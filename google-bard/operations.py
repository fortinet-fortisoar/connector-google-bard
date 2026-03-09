"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

import requests, json, logging
from requests_toolbelt.utils import dump
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('google-bard')
logger.setLevel(logging.INFO)

class GoogleGemini(object):
    def __init__(self, config, *args, **kwargs):
        self.api_key = config.get('api_key')
        url = config.get('server_url').strip('/')
        if not url.startswith('https://') and not url.startswith('http://'):
            self.url = 'https://{0}/v1beta/models'.format(url)
        else:
            self.url = url + '/v1beta/models'
        self.verify_ssl = config.get('verify_ssl')

    def make_rest_call(self, url, method, data=None, params=None):
        try:
            url = self.url + url + '?key={0}'.format(self.api_key)
            headers = {
                'Content-Type': 'application/json'
            }
            logger.debug("Endpoint {0}".format(url))
            response = requests.request(method, url, data=data, params=params, headers=headers, verify=self.verify_ssl)
            logger.debug('\n{0}\n'.format(dump.dump_all(response).decode('utf-8')))
            if response.ok or response.status_code == 204:
                logger.info('Successfully got response for url {0}'.format(url))
                if 'json' in str(response.headers):
                    return response.json()
                else:
                    return response
            elif response.status_code == 404:
                return response
            else:
                logger.error("{0}".format(response.status_code))
                raise ConnectorError("{0}:{1}".format(response.status_code, response.text))
        except requests.exceptions.SSLError:
            raise ConnectorError('SSL certificate validation failed')
        except requests.exceptions.ConnectTimeout:
            raise ConnectorError('The request timed out while trying to connect to the server')
        except requests.exceptions.ReadTimeout:
            raise ConnectorError(
                'The server did not send any data in the allotted amount of time')
        except requests.exceptions.ConnectionError:
            raise ConnectorError('Invalid Credentials')
        except Exception as err:
            raise ConnectorError(str(err))


def check_payload(payload):
    updated_payload = {}
    for key, value in payload.items():
        if isinstance(value, dict):
            nested = check_payload(value)
            if len(nested.keys()) > 0:
                updated_payload[key] = nested
        elif value != '' and value is not None:
            updated_payload[key] = value
    return updated_payload


def create_model_name(model_name):
    if 'models/' in model_name:
        model_name = model_name.split("models/")[1]
    return model_name


def list_models(config, params):
    try:
        gb = GoogleGemini(config)
        endpoint = ''
        query_params = {k: v for k, v in params.items() if v is not None and v != ''}
        response = gb.make_rest_call(endpoint, 'GET', params=query_params)
        return response
    except Exception as err:
        raise ConnectorError(str(err))


def get_model_details(config, params):
    try:
        gb = GoogleGemini(config)
        model_name = create_model_name(params.pop('name'))
        endpoint = '/{0}'.format(model_name)
        query_params = {k: v for k, v in params.items() if v is not None and v != ''}
        response = gb.make_rest_call(endpoint, 'GET', params=query_params)
        return response
    except Exception as err:
        raise ConnectorError(str(err))


def generate_text(config, params):
    try:
        gb = GoogleGemini(config)
        model_name = create_model_name(params.pop('name')) 
        endpoint = '/{0}'.format(model_name) + ':generateContent'
        contents = params.get('contents')
        payload = {
            "contents": contents if isinstance(contents,list) else [contents],
            "generationConfig": {
                "stopSequences": list(params.get('stopSequences')) if params.get('stopSequences') else None,
                "temperature": float(params.get('temperature')) if params.get('temperature') else None,
                "maxOutputTokens": int(params.get('maxOutputTokens')) if params.get('maxOutputTokens') else None,
                "topP": float(params.get('topP')) if params.get('topP') else None,
                "topK": int(params.get('topK')) if params.get('topP') else None
            },
            "safetySettings": params.get('safetySettings') if isinstance(params.get('safetySettings'),list) else None
        }
        system_instruction = params.get('system_instruction')
        if system_instruction:
            payload.update({
                    "system_instruction": {
                        "parts": [
                            {
                            "text": system_instruction
                            }
                        ]
                    }
            })
        thinkingLevel = params.get('thinkingLevel')
        if thinkingLevel:
            payload["generationConfig"].update({
                "thinkingConfig": {
                        "includeThoughts": True,
                        "thinkingLevel": thinkingLevel
                    }
            })
        # Clean up empty params
        payload = {k: v for k, v in payload.items() if v is not None}
        if "generationConfig" in payload:
            payload["generationConfig"] = {k: v for k, v in payload["generationConfig"].items() if v is not None}

        response = gb.make_rest_call(endpoint, 'POST', data=json.dumps(payload), params={})
        return response
    except Exception as err:
        raise ConnectorError(str(err))


def generate_embeddings(config, params):
    try:
        gb = GoogleGemini(config)
        model_name = create_model_name(params.pop('name'))
        endpoint = '/{0}'.format(model_name) + ':embedContent'
        content = params.get('content')
        payload = {
                "content": {
                    "parts": [
                    { "text": content }
                    ]
                }
        }
        taskType = params.get('taskType')
        if taskType:
            payload.update({
                "taskType": taskType
            })
        outputDimensionality = params.get('outputDimensionality')
        if outputDimensionality:
            payload.update({
                "outputDimensionality": outputDimensionality
            })
        
        response = gb.make_rest_call(endpoint, 'POST', data=json.dumps(payload), params={})
        return response
    except Exception as err:
        raise ConnectorError(str(err))


def count_message_token(config, params):
    try:
        gb = GoogleGemini(config)
        # 'gemini-3.1-flash-lite-preview' or newer model should be used as the old bard models are retired
        model_name = create_model_name(params.pop('name'))
        endpoint = '/{0}'.format(model_name) + ':countTokens'
        system_instruction = params.get('system_instruction')
        payload = {
            "contents": params.get('messages')
        }
                    
        response = gb.make_rest_call(endpoint, 'POST', data=json.dumps(payload), params={})
        return response
        
    except Exception as err:
        # Better error reporting for debugging API changes
        raise ConnectorError(f"Gemini Token Count Failed: {str(err)}")


def check_health(config):
    try:
        response = list_models(config, params={'pageSize': 1})
        if response:
            return True
    except Exception as err:
        logger.info(str(err))
        raise ConnectorError(str(err))


operations = {
    'list_models': list_models,
    'get_model_details': get_model_details,
    'generate_text': generate_text,
    'generate_embeddings': generate_embeddings,
    'count_message_token': count_message_token
}
