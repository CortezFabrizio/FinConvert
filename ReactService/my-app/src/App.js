

import './App.css';
import React, { useState } from 'react';


function App() {

  const [fin_data,setFin_data] = useState(null);
  const [ticker_value,setTicker] = useState(null);
  const [start_date,setStart] = useState(null);
  const [end_date,setEnd] = useState(null);

  return (
    <div id="searcher" className="App">

      <label>
        Ticker Symbol
          <input id='ticker' type="text"></input>
      </label>

      <label>
        Starting year
        <input id='start_date' type="text"></input>
      </label>

      <label> 
       Ending year
        <input id='end_date' type="text"></input>
      </label>

      <input type="button" value="Search" onClick={

        async () => {
          const ticker_value = document.getElementById("ticker").value;
          setTicker(ticker_value)
          const start_date = document.getElementById("start_date").value;
          setStart(start_date)
          const end_date = document.getElementById("end_date").value;
          setEnd(end_date)


          const finanicals = await get_financials(ticker_value,start_date,end_date);
          setFin_data(finanicals);
        }

      } > 
      </input>

      {fin_data &&
      
        <div id='results'>

            <button type="button" className="btn btn-success"> <a className="link-light" href={'http:/FutureExternalIpHere/create-excel?ticker='+ticker_value+'&start_date='+start_date+'&end_date='+end_date }>Download Excel</a> </button>
      
            { fin_data }
        </div> 
      }
      
    </div>
  );
}


async function get_financials(ticker_value,start_date,end_date) {

  const url = new URL ('http://FutureExternalIpHere/get-ticker')
  
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



  function renderStatementRows(statement) {
    const rows = [];
  
    Object.keys(statement).forEach((conceptTitle, index) => {
      if (conceptTitle === 'title') {
        return;
      }
  
      const concepts = statement[conceptTitle];
      rows.push(<tr key={`statement-${index}-row1`}><td align='left'><b>{conceptTitle}</b></td><td></td></tr>);
  
      Object.keys(concepts).forEach((key, subIndex) => {
        const value = concepts[key];
        rows.push(<tr key={`statement-${index}-row2-${subIndex}`}><td className='w-25' align='left'>{key}</td><td>{value}</td></tr>);
      });
    });
  
    return rows;
  }
  
  function renderStatement(statementValues, year, sheet) {
    return (
      <div className="accordion-item" key={`${year}-${sheet}`}>
        <h2 className="accordion-header" id={`panel${year}${sheet}`}>
          <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target={`#collapse${year}${sheet}`} aria-expanded="false" aria-controls={`collapse${year}${sheet}`}>
            {statementValues['title']}
          </button>
        </h2>
        <div id={`collapse${year}${sheet}`} className="accordion-collapse collapse" aria-labelledby={`panel${year}${sheet}`}>
          <div className="accordion-body">
            <table className='table table-bordered table-hover w-100 h-25'>

              <tbody>
                {renderStatementRows(statementValues)}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }
  
  function renderYear(year, req) {
    const statements = req[year];
    return (
      <div className="accordion-item" key={year}>
        <h2 className="accordion-header" id={`panel${year}`}>
          <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target={`#collapse${year}`} aria-expanded="false" aria-controls={`collapse${year}`}>
            {year}
          </button>
        </h2>
        <div id={`collapse${year}`} className="accordion-collapse collapse" aria-labelledby={`panel${year}`}>
          <div className="accordion-body">
            <div className='accordion'>
              {Object.keys(statements).map((sheet) => renderStatement(statements[sheet], year, sheet))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const financialTables = (
    <div className='accordion'>
      { Object.keys(req).map((year) => renderYear(year, req))}
    </div>
  );

   return (financialTables)

    };


export default App;
