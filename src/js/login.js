const formElement = document.querySelector('form');
const emailInput = document.querySelector("#email")
const passwordInput = document.querySelector("#password")
const messageElement = document.querySelector("#message")

formElement.addEventListener('submit', (event) => {
    event.preventDefault();
    login(emailInput.value , passwordInput.value)
});

async function login(email , password){
   await fetch("http://localhost:5000/login" , {
    method: "POST",
    body: JSON.stringify({
        "email": email,
        "password": password 
    }),
    headers: {
     "content-type": "application/json" 
    }
   }).then(response => response.json()).then(data => {
    messageElement.textContent = data.message
   }).catch(error => {
    console.log(error)
   })
}