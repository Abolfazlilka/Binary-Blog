const formElement = document.querySelector('form');
const fullNameInput = document.querySelector('#fullname')
const emailInput = document.querySelector("#email")
const passwordInput = document.querySelector("#password")
const messageElement = document.querySelector("#message")

formElement.addEventListener('submit', (event) => {
    event.preventDefault();
    register(fullNameInput.value , emailInput.value , passwordInput.value)
});

async function register(name , email , password){
   await fetch("/register" , {
    method: "POST",
    body: JSON.stringify({
        "email": email,
        "fullname": name,
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