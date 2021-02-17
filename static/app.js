let username = document.querySelector('#username').innerHTML

async function processForm(evt) {
    evt.preventDefault()
    let search = $("#recipe").val()
    let filter = []
    protein.checked ? filter.push('high-protein') : ''
    low_fat.checked ? filter.push('low-fat') : ''
    low_carb.checked ? filter.push('low-carb') : ''

    try {
        let response = await axios.post("/recipes", { params: search, filter: filter });
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
            "url": url,
            "calories": calories,
            "yield": yield,
            "time": time,
            "ingredients": ingredients
        }
        
        let card = `
        <div class="card col-md-4 p-3">
            <div class="col-md-12">
                <img class="card-img-top" src="${image}" alt="${title}">
                <div class="col card-body">
                    <h5 class="card-title">${title}</h5>
                    <p class="card-text">Source: ${source}</p>
                    <a href="${url}" class="btn btn-info" target="_blank">Full Recipe</a>
                    ${username ? `<button id="${index}" class="btn btn-primary">Save Recipe</button>` : ''}
                </div>
            </div>
        </div>`
            $('.recipe-list').append(card);
            if (username) {
                document.getElementById(`${index}`).addEventListener('click', async function () {
                    try {
                        let response = await axios.post(`/users/${username}/recipes/new`, { params: recipeObj });
                        alert(response['data']['message'])
                    } catch (e) {
                        console.log(e);
                    }            
                });
            }
    }
}

$("#recipe-search").on("submit", processForm)
