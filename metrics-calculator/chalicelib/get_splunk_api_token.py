def get_splunk_api_token(ssm, parameter_name):
    parameter_details = ssm.get_parameter(Name=parameter_name)
    return parameter_details['Parameter']['Value']