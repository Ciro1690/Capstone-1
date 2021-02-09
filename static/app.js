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
    let recipes = resp['data']['hits']
    for (let recipeInfo of recipes) {
        let recipe = recipeInfo['recipe']
        
        let image = recipe['image']
        let title = recipe['label']
        let calories = Math.round(recipe['calories'])
        let url = recipe['url']
        let yield = recipe['yield']
        let time = recipe['totalTime'] === 0 ? null : recipe['totalTime']
        let ingredients = recipe['ingredientLines']
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
                <p class="card-text">Calories: ${calories}</p>
                <p class="card-text">Yield: ${yield} servings</p>
                <a href="${url}" class="btn btn-info" target="_blank">Full Recipe</a>
                <button id="save-recipe" class="btn btn-primary">Save Recipe</button>
                </div>
            </div>`
            $('.recipes-list').append(card);
    }
}

$("#recipe-search").on("submit", processForm)