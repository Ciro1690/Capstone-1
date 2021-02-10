let username = document.querySelector('#username').innerHTML

async function processForm(evt) {
    evt.preventDefault()
    let search = $("#recipe").val()

    try {
        let response = await axios.post("/recipes", { params: search });
        handleResponse(response)
    } catch (e) {
        console.log(e);
    }
}

function handleResponse(resp) {
    $('.recipe-list').empty()
    let recipes = resp['data']['hits']
    for (let recipeInfo of recipes) {
        let recipe = recipeInfo['recipe']
        
        let image = recipe['image']
        let index = recipes.indexOf(recipeInfo)
        let title = recipe['label']
        let calories = Math.round(recipe['calories'])
        let url = recipe['url']
        let yield = recipe['yield']
        let time = recipe['totalTime'] === 0 ? null : recipe['totalTime']
        let ingredients = recipe['ingredientLines']
        let source = recipe['source']

        let recipeObj = {
            "title": title,
            "image": image,
            "calories": calories,
            "yield": yield,
            "time": time,
            "ingredients": ingredients
        }
        
        let card = `
        <div class="card m-3" style="width: 18rem;">
            <img class="card-img-top" src="${image}" alt="${title}">
            <div class="col card-body">
                <h5 class="card-title">${title}</h5>
                <p class="card-text">Source: ${source}</p>
                <a href="${url}" class="btn btn-info" target="_blank">Full Recipe</a>
                ${username ? `<button id="${index}" class="btn btn-primary">Save Recipe</button>` : ''}
                </div>
            </div>`
            $('.recipe-list').append(card);
            if (username) {
                document.getElementById(`${index}`).addEventListener('click', async function () {
                    try {
                        await axios.post(`/users/${username}/recipes/new`, { params: recipeObj });
                    } catch (e) {
                        console.log(e);
                    }            
                });
            }
    }
}

$("#recipe-search").on("submit", processForm)
