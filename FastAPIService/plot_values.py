import requests
import os
import json
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('agg')

#######################################


# WARNING

# This feature is still in development,endpoint is not publicly available , SEC data needs 
#  more processing and labeling to cover all companies . 




##################################

save_plot_image_in = os.getenv('PLOTS_PATH')

def plot_concept (ticker,start_date,end_date,income_concept):

    income_concept = 'dsfdsgsg'

    param = {'ticker':ticker,'start_date':start_date,'end_date':end_date}

    #Getting finanical data using my FastAPI route in the same server
    req = requests.get('http://127.0.0.1:8000/get-ticker',param)

    financials = json.loads(req.json())

    data_to_plot = {}

    for year in financials:
        data_to_plot[year] = {}

        income_first_values = financials[year]['Income']['FirstBlock']

        if income_concept in income_first_values:

            concept_value = financials[year]['Income']['FirstBlock'][income_concept]

            data_to_plot[year] = {income_concept:concept_value}
            continue
            

        else:
            return Exception("Concept does not exist")

        
    dataframe = pd.DataFrame.from_dict(data_to_plot,orient='index')

    dataframe.index = pd.to_datetime(dataframe.index)

    plt.plot(dataframe.index, dataframe['Net sales'])

    plt.xlabel('Years')
    plt.ylabel('Net sales')
    plt.title('Net Sales over time')

    path_to_image = save_plot_image_in+f'{ticker}.png'

    plt.savefig(path_to_image,format='png')

    return path_to_image
    




