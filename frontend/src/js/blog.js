window.addEventListener('DOMContentLoaded' , event => {
    fetchBlog()
})

const coverEl = document.querySelector("#cover")
const titleEl = document.querySelector('#title')
const authorEl = document.querySelector("#author")
const publishedEl = document.querySelector("#publishedAt")
const articleData = document.querySelector("article p")

async function fetchBlog(){
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');
    await fetch(`/post/${id}`, {
        method: "GET",
    }).then(res => res.json()).then(data => {
        console.log(data)
        authorEl.textContent = data.author
        coverEl.src = data.image
        titleEl.textContent = data.title
        publishedEl.textContent = data.published_at
        articleData.textContent = data.caption
    })
}