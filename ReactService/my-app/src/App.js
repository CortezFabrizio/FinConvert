
import './App.css';
import React, { useState } from 'react';


function App() {

  const [fin_data,setFin_data] = useState(null);

  return (
    <div id="searcher" className="App">
      <p>Hello World</p>

      <input id='ticker' type="text"></input>
      <input id='end_date' type="text"></input>
      <input id='start_date' type="text"></input>

      <input type="button" value="Search" onClick={

        async () => { 
          const finanicals = await get_financials();
          setFin_data(finanicals);
        }
      } > 
      </input>
 
      {fin_data && <div id='results'> { fin_data } </div> }
      
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


  const years = Object.keys(req);

  const financialTables = (
    <div className="accordion">
      {years.map((year) => {
        const statements = req[year];
        return (
          <div key={year} className="accordion-item">
            <h2 className="accordion-header" id={`panel${year}`}>
              <button
                className="accordion-button collapsed"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target={`#collapse${year}`}
                aria-expanded="false"
                aria-controls={`collapse${year}`}
              >
                {year}
              </button>
            </h2>

            <div
              id={`collapse${year}`}
              className="accordion-collapse collapse"
              aria-labelledby={`panel${year}`}
            >
              <div className="accordion-body">
                <div className="accordion">
                  {Object.keys(statements).map((sheet) => {
                    const statement = statements[sheet];

                    return (
                      <div key={sheet} className="accordion-item">
                        <h2
                          className="accordion-header"
                          id={`panel${year}${sheet}`}
                        >
                          <button
                            className="accordion-button collapsed"
                            type="button"
                            data-bs-toggle="collapse"
                            data-bs-target={`#collapse${year}${sheet}`}
                            aria-expanded="false"
                            aria-controls={`collapse${year}${sheet}`}
                          >
                            {sheet}
                          </button>
                        </h2>

                        <div
                          id={`collapse${year}${sheet}`}
                          className="accordion-collapse collapse"
                          aria-labelledby={`panel${year}${sheet}`}
                        >
                          <div className="accordion-body">
                            <table className="table table-bordered table-hover w-100 h-25">
                              <thead>
                                <tr>
                                  <th colSpan="2" scope="col">
                                    {statement["title"]}
                                  </th>
                                </tr>
                                {delete statement["title"]}
                              </thead>
                              <tbody>
                                {Object.keys(statement).map((conceptTitle) => {
                                  if (conceptTitle === "title") {
                                    return null;
                                  }

                                  const concepts = statement[conceptTitle];
                                  const rows = [
                                    <tr key={conceptTitle}>
                                      <td align="left">
                                        <b>{conceptTitle}</b>
                                      </td>
                                      <td></td>
                                    </tr>,
                                  ];
                                  const conceptKeys = Object.keys(concepts);

                                  conceptKeys.forEach((keyy) => {
                                    const valueConcept = concepts[keyy];

                                    rows.push(
                                      <tr key={keyy}>
                                        <td className="w-25" align="left">
                                          {keyy}
                                        </td>
                                        <td>{valueConcept}</td>
                                      </tr>
                                    );
                                  });
                                  return rows;
                                })}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );

   return (financialTables)

    };


export default App;
