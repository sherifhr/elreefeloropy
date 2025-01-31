var table = document.getElementById('farm-list');
var selectedCells = [];

for (var i = 0; i < table.rows.length; i++) {
    var row = table.rows[i];
    var cell5 = row.cells[5];
    //selectedCells6.push(cell6.textContent);
    selectedCells.push(cell5.textContent);
  
    //selectedCells.push(cell5.textContent +'-'+ cell6.textContent);
  }
const uniqueItemsSet   = new Set(selectedCells);
const uniqueItemsArray = Array.from(uniqueItemsSet);

for (var i = 0; i <uniqueItemsArray.length; i++) {
    console.log(uniqueItemsArray);
    document.getElementById("result"+i).textContent =uniqueItemsArray[i].toString();     
}

function assignValue() {
    var dropdown = document.getElementById('myDropdown');
    var selectedOption = dropdown.options[dropdown.selectedIndex];
    var selectedValue = selectedOption.value;
    var input = document.getElementById('myInput');
    input.value= dropdown.options[dropdown.selectedIndex].text;  
}
// console.log(selectedValue);
console.log('Before pause');
setTimeout(function() {
console.log('After 3 seconds');
}, 3000);


function myFunction() {
  var x = document.getElementById("myTopnav");
  if (x.className === "topnav") {
    x.className += " responsive";
  } else {
    x.className = "topnav";
  }
}

  function checkLogin() {
  // Assume you have a variable or function to check the user's login status
  var isLoggedIn = checkUserLoginStatus();

  var link = document.getElementById('myLink');

  if (isLoggedIn) {
    link.href="{{url_for('login')}}"  // Set the link URL
    link.removeAttribute('disabled');  // Remove the disabled attribute
  } else {
    link.removeAttribute('href');       // Remove the link URL
    link.setAttribute('disabled', 'disabled');  // Add the disabled attribute
  }
  }
  function submitForm(){
    document.getElementById("myForm").submit();
    }

    function submitForm1(){
    document.getElementById("myForm1").submit();
    }

    document.addEventListener("DOMContentLoaded", function() {
      updateEntry() });
    
    function updateEntry(){
      const mainSelect = document.getElementById('options');
      const subSelect = document.getElementById('options');
         // Clear existing options
            options.innerHTML = '';
    }
  function checkLogin() {
  // Assume you have a variable or function to check the user's login status
  var isLoggedIn = checkUserLoginStatus();

  var link = document.getElementById('myLink');

  if (isLoggedIn) {
    link.href="{{url_for('login')}}"  // Set the link URL
    link.removeAttribute('disabled');  // Remove the disabled attribute
  } else {
    link.removeAttribute('href');       // Remove the link URL
    link.setAttribute('disabled', 'disabled');  // Add the disabled attribute
  }
  }


