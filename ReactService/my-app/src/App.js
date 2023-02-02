
import './App.css';
import React, { Component } from 'react';
import  ReactDOM  from 'react-dom';


function send_api() {
  const ticker_value = document.getElementById("ticker").value;
  const start_date = document.getElementById("end_date").value;
  const end_date = document.getElementById("start_date").value;

  const url = new URL ('http://0.0.0.0:80/get-ticker')
  
  const params = {'ticker':ticker_value,'start_date':start_date,'end_date':end_date}
  url.search = new URLSearchParams(params).toString();


  const info = {
    method:"GET",
    header:{'Access-Control-Allow-Origin':'*'}
  }

  const req = fetch(url,info).then(function DD(response){
    //const res = response.json()

    console.log(response.json() ,typeof(response))
    return response


   })   ;

}

function App() {
  return (
    <div id="lolo" className="App">
      <p>Hola Mundo</p>

      <input id='ticker' type="text"></input>
      <input id='end_date' type="text"></input>
      <input id='start_date' type="text"></input>

      <input type={"button"} value="Search" onClick={send_api} ></input>
      
    </div>
  );
}

export default App;

