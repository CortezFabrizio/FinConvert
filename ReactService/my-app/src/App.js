
import './App.css';
import React, { Component } from 'react';
import  ReactDOM  from 'react-dom';



function f() {
  const ge = document.getElementById("oi").value;
  
  const url = null
  
  const po = {ticker:ge}

  const info = {
    method:"POST",
    body: JSON.stringify(po),
    headers: {"Content-Type":"application/json"}
  }

  const yy = fetch(url,info).then(function DD(response){
    const res = response.json()
    console.log(res)
    return res
    
   });

}

function App() {
  return (
    <div id="lolo" className="App">
      <p>Hola Mundo</p>
      <input id='oi' type="text"></input>
      <input type={"button"} value="Search" onClick={f} ></input>
      
    </div>
  );
}

export default App;
