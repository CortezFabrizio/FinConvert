import './App.css';
import React, { useState , useEffect } from 'react';
import logo from './finconvert.png'
import git_logo from './git_logo.png'
import { DebounceInput } from 'react-debounce-input'


function LoadingEffect(props){
  if (props.isLoading === false){

    return (
    <div className="spinner-border text-success m-5" role="status">
      <span className="sr-only">Loading...</span>
    </div>
    )

  }
}

function Intro(props){
  if (props.initial === 'initialStyle' && !(props.err)){

    return (
        <div className="card" style={{width:'70%',margin:'auto'}}>
          <div className="card-body">
            <p><span style={{color:'red'}}>English</span>: FinConvert will return Income,Balance and Cash flow statements,as a excel too,from 2013 to the present,where the company name or ticker symbol represents a U.S based and publicly trading company(each company has a unique one assigned by the SEC). <span style={{color:'red'}}>Usage example with the company Amazon.com,Inc: Ticker Symbol = AMZN , Starting year = 2017 , Ending year = 2022.The correlation between company names and tickers is not always consistent (name: Alphabet Inc., ticker: GOOGL).</span></p>
            <p><span style={{color:'red'}}>Español</span>:FinConvert devolverá los estados de ingresos, balances y flujos de efectivo, también en formato Excel, desde 2013 hasta la actualidad, donde el "Ticker Symbol" o nombre de la empresa representa una empresa con sede en Estados Unidos y cotizada públicamente(cada empresa tiene una asignada por la SEC).Buscando por nombre de empresa es posible<span style={{color:'red'}}>Por ejemplo en el caso de Netflix : Ticker Symbol = NFLX , Starting year = 2013 , Ending year = 2019.No siempre hay correlación entre los nombres de las empresas y los tickers (nombre: Alphabet Inc., ticker: GOOGL).</span></p>
        </div>
      </div>
      )
  }

}

function RepoLogo(){

  return (
  <a href='https://github.com/CortezFabrizio/FinConvert' style={{display:'block',width:'120px',margin:'auto'}} >
        <figure style={{marginTop:'20px'}} >
          <img alth='git logo' src={git_logo} className='github'></img>
          <figcaption style={{fontSize:'70%'}}>Architecture diagram and Github repository</figcaption>
        </figure>
  </a>
  )
  
}


function App() {

  const [fin_data,setFin_data] = useState(null);
  const [ticker_value,setTicker] = useState(null);
  const [start_date,setStart] = useState(null);
  const [end_date,setEnd] = useState(null);
  const [validation_error,setError] = useState(null);
  const [initial_style,setStyle] = useState(['initialStyle','logo','font','title','justify-content-center'])

  return (
    <div id="searcher" className={`App`}>

  <div className={`${initial_style[0]}`}>

      <nav className={`navbar p-0 navBack ${initial_style[4]}`}>

        <a><img alt='image' className={initial_style[1]} src={logo}></img>
        </a>
        
        <a className={initial_style[3]}><h2 className={`${initial_style[2]} mb-0`}>FinConvert</h2>
          <p style={{fontSize:'60%'}}>By: Fabrizio Cortez <br></br>fabriziocortezandres@gmail.com</p>

          {initial_style[0] === 'initialStyle' &&
             <p style={{fontSize:'60%',margin:'0px',color:'red'}}>Read footer for more information / Leer footer </p>
          }

          
        </a>

      </nav>

    <form className='form-inline justify-content-center'>  

          <SearchAutocomplete></SearchAutocomplete>


        <div className='form-floating m-3'>
          <input id='start_date' type="text" className='form-control' placeholder='.'></input>
          <label for='start_date'>Starting year </label>

        </div>

        <div className='form-floating m-3'>

          <input id='end_date' type="text" className='form-control' placeholder='.'></input>
          <label for='end_date'> Ending year </label>

        </div>

  
        <input type="button" className='btn btn-outline-secondary btn-lg' value="Search" onClick={
        async () => {

          setFin_data(false)
          const ticker_valu = document.getElementById("ticker").value;

          setTicker(ticker_valu)

          const start_date = document.getElementById("start_date").value;
          setStart(start_date)
          const end_date = document.getElementById("end_date").value;
          setEnd(end_date)

          const finanicals = await get_financials(ticker_valu,start_date,end_date);

          if (!(finanicals[0])){
            setError(finanicals[1])
            setFin_data(null)
          }
          else{
            setStyle(['secondStyle','logoTransition','secondFont','titleTransition',null])
            setError(null)
            setFin_data(finanicals[1]);
          }
        }

        } > 
        </input>  
         
        </form>  

  </div>
      <LoadingEffect isLoading={fin_data}></LoadingEffect>
      <RepoLogo></RepoLogo>
      <Intro initial={initial_style[0]} err={validation_error}></Intro>

      {fin_data &&
      
        <div id='results' className='m-3'>

            <button type="button" className="btn btn-success m-4"> <a className="link-light" href={'http://54.214.244.209/create-excel?ticker='+ticker_value+'&start_date='+start_date+'&end_date='+end_date }>Download Excel</a> </button>
      
            { fin_data }
        </div>
      }

      {validation_error &&

      <div id='errors' className='card' style={{width:'60vw',margin:'auto',marginTop:'1px',backgroundColor:'#ff4d4d',color:'black'}}>    
        <div className='card-body'>
          <ul>
            <strong>
            { validation_error }
            </strong>
          </ul>
        </div>
      </div> 
      }   

    </div>

  );

}


async function get_financials(ticker_value,start_date,end_date) {

  const url = new URL ('http://54.214.244.209/get-ticker')
  
  const params = {'ticker':ticker_value,'start_date':start_date,'end_date':end_date}
  url.search = new URLSearchParams(params).toString();

  const info = {
    method:"GET",
    header:{'Access-Control-Allow-Origin':'*'}
  };

   const req = await fetch(url,info).then((response) => {
    if (!response.ok) {
      return response.json().then(res => { throw Error(JSON.stringify(res)) });
    }

    return response.json()

    })
    .then((responseJSON) => {

    const financial_object = JSON.parse(responseJSON);

    return financial_object
  
    }

    ).catch(error => {

      return error

    });



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

  if ( !(req instanceof Error) ){
    const financialTables = (
      <div className='accordion'>
        { Object.keys(req).map((year) => renderYear(year, req))}
      </div>
    );

   return ([true,financialTables])

  }

  else{
    const validation_errors = JSON.parse(req.message);
    const error_message_user =  [];
    for (const error in validation_errors){

      if (error  === 'detail'){
        error_message_user.push(<li>{validation_errors[error]}</li>);
      }
      else{     
         error_message_user.push(<li>{error}:{validation_errors[error]}</li>);
    }

    }

    return [false,error_message_user]
  }

  };


  function SearchAutocomplete() {
    const [userInput, setUserInput] = useState(null);
    const [suggestions, setSuggestions] = useState(null);
    const [selectedTicker,setSelTicker] = useState('');

    useEffect(() => {
      const fetchSuggestions = async () => {
        try {
          const response = await fetch(`http://54.214.244.209/search-name?Typed=${userInput}`,{
            method: 'GET',
          });

          const data = await response.json();
          setSuggestions(JSON.parse(data));
        } catch (error) {
          console.error(error);
        }
      };

      if (userInput){
        fetchSuggestions();
      }

    }, [userInput]);
  
    const handleInputChange = (event) => {
      setSelTicker(event.target.value);
      setUserInput(event.target.value);
    };

    function setValue (ticker){
      setSelTicker(ticker);
 
      document.getElementById('suggestions').style.display = 'none';
    }


    const handle_results = function handle (item){
      if ('ticker' in item){
        return   <a key={item['ticker']} href="#" style={{margin:'auto'}} onClick={() => setValue(item['ticker'])} className="list-group-item list-group-item-action">{item['name']}</a>
      }
    }


    function blur (){
      if(!(document.getElementById('suggestions').style.display === 'none')){
        setTimeout(() => {
          document.getElementById('suggestions').style.display = 'none';
        }, 200);
    }
  }


    return (
      <div>

        <div className='form-floating m-3'>
        <DebounceInput
          id='ticker'
          type='text'
          value={selectedTicker}
          placeholder='.'
          onBlur={blur}
          onClick={()=>{document.getElementById('suggestions').style.display='block'}}
          className='form-control'
          minLength={1}
          debounceTimeout={220}
          onChange={handleInputChange}
        />

          <label for='ticker'>Company name or ticker</label>

          <ul style={{width:'100%',position:'absolute',zIndex:1000,display:'none'}} className='list-group list-group-flush' id='suggestions'>
            <a href="#" style={{margin:'auto',fontSize:'70%'}} className="list-group-item list-group-item-action">Type a name or ticker and select a US company:</a>          
            {suggestions ? suggestions.map((suggestion) => handle_results(suggestion)) : null}
        </ul>

        </div>

      </div>
    );
  }

export default App;
