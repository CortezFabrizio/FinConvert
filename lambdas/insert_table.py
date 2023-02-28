import json
import boto3

def insert_table(event,context):
    table = boto3.resource('dynamodb').Table('fabri_app')
    
    message = event['Records'][0]
    
    statements_results = json.loads(message['body'])
    ticker = message['messageAttributes']['ticker']['stringValue']
    
    def_value_year = ':def_year_value'

    update_expression = ''
    update_values = {}
    update_names = {}

    update_expression_years = ''
    update_values_years = {def_value_year:{}}

    for year in statements_results:

        if update_expression_years:
            update_expression_years+= f', #{year} = {def_value_year}'
        else:
            update_expression_years+= f'SET #{year} = {def_value_year}'

        statements = statements_results[year]

        for statement in statements:                    

            sheet = json.dumps(statements[statement])

            attr_value = f':{year}{statement}'

            if f'#{year}' not in update_names:
                update_names[f'#{year}'] = year


            if update_expression:
                update_expression += f', #{year}.{statement} = {attr_value}'
                update_values[attr_value] = sheet

            else:
                update_expression += f'SET #{year}.{statement} = {attr_value}'
                update_values[attr_value] = sheet


    table.update_item(
        Key={
            'ticker':ticker
        },
        UpdateExpression=update_expression_years,

        ExpressionAttributeNames=update_names,

        ExpressionAttributeValues=
            update_values_years,
    )


    table.update_item(
        Key={
            'ticker': ticker
        },
        UpdateExpression=update_expression,

        ExpressionAttributeNames=update_names,

        ExpressionAttributeValues=
            update_values,
    )

