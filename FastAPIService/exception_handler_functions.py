
def error_validation_response(exc):

    list_errors = exc.errors()

    error_response = {}

    for desc_error in list_errors:
        parameter_values = {'start_date':'Starting year','end_date':'Ending year','ticker':'Ticker symbol'}

        parameter =  parameter_values[desc_error['loc'][1]]
        error_type = desc_error['type']

        if error_type == 'value_error.missing':
            error_response[parameter] = 'value is missing'

        elif error_type == 'type_error.integer':
            error_response[parameter] = 'value must be a integer'

        elif error_type == 'type_error.string':
            error_response[parameter] = 'value must be a string'
    
    return error_response
