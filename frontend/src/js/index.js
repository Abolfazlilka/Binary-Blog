window.addEventListener('DOMContentLoaded' , event => {
    fetchBlogs()
})

const articleEl = document.querySelector('article')

async function fetchBlogs(){
    await fetch('/allposts' , {
        method: "GET",
    }).then(res => res.json())
    .then(data => {
        data.forEach(blog => {
            console.log(blog)
            const blogCard = createBlogCard(blog)
            appendBlogCard(blogCard)
        });
    });
}

function createBlogCard(blog){
    const blogCard = `
    <a href="./blog.html?id=${blog.id}" target="_blank" class="blog-card">
        <div class="blog-card-image">
            <img src="${blog.image}" alt="${blog.title}">
        </div>
        <div class="blog-card-author">
            <p>${blog.published_at.split('T')[0]}</p>
            <p>${blog.author}</p>
        </div>
        <div class="blog-card-content">
            <h3>${blog.title}</h3>
            <p>${blog.caption}</p>
        </div>
    </a>
    `
    return blogCard
}

function appendBlogCard(blogCard){
    articleEl.innerHTML += blogCard
}