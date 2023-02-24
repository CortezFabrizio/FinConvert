
import './App.css';
import React, { useState } from 'react';
import  ReactDOM  from 'react-dom/client';


function App() {

  const [fin_data,setFin_data] = useState(null);

  return (
    <div id="searcher" className="App">
      <p>Hola Mundo</p>

      <input id='ticker' type="text"></input>
      <input id='end_date' type="text"></input>
      <input id='start_date' type="text"></input>

      <input type="button" value="Search" onClick={ 

        async () => { 
          const finanicals = await get_financials();
          setFin_data(finanicals)
        }
      } > 
      </input>

      {fin_data
      ?
      <div id='results'>
          {fin_data}
      </div>
      : 
        <p></p>
      }

    </div>
  );
}


async function get_financials() {

  const ticker_value = document.getElementById("ticker").value;
  const start_date = document.getElementById("end_date").value;
  const end_date = document.getElementById("start_date").value;

  const url = new URL ('http://0.0.0.0:80/get-ticker')
  
  const params = {'ticker':ticker_value,'start_date':start_date,'end_date':end_date}
  url.search = new URLSearchParams(params).toString();

  const info = {
    method:"GET",
    header:{'Access-Control-Allow-Origin':'*'}
  };

   const req = await fetch(url,info).then((response) => {
    return response.json()

    })
    .then((responseJSON) => {

    const financial_object = JSON.parse(responseJSON);

    return financial_object
  
    }

    );


   const financial_tables = Object.keys(req).map( (year) =>
      {

        const statements = req[year];
        return ( Object.keys(statements).map((sheet)=>{
          const statement = statements[sheet]

          return(
            <table style={{border: "1px solid black"}}>
                <tbody>
                  <tr>{statement['title']}</tr>
                      {delete statement['title']}
                      {Object.keys(statement).map(
                        (concept_title)=>{
                            
                            const concepts = statement[concept_title];
                            const rows = [<tr><td>{concept_title}</td></tr>]
                            const concept_keys = Object.keys(concepts)

                            concept_keys.forEach((keyy)=>{
                              
                              const value_concept = concepts[keyy];

                              rows.push(<tr><td>{keyy}</td><td>{value_concept}</td></tr>)                        
                            })
                            return rows                                  
                        }
                       )                                                               
                      }

                </tbody>

            </table>
          )

        }))

      }

   )
     
   return (financial_tables)

    };

export default App;
