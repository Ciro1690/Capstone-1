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
    console.log(recipes)
    if (recipes.length === 0) {
        alert("Sorry, your search produced no results.")
    } else {
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
            <div class="card-outer col-md-4">
                <div class="card-inner">
                    <img class="card-img-top" src="${image}" alt="No image available">
                    <div class="col card-body">
                        <h5 class="card-title">${title}</h5>
                        <p class="card-text">Source: ${source}</p>
                        <a href="${url}" class="btn btn-info" target="_blank">Full Recipe</a>
                        ${username !== 'Login' ? `<button id="${index}" class="btn btn-primary">Save Recipe</button>` : ''}
                    </div>
                </div>
            </div>`
            $('.recipe-list').append(card);
            if (username !== 'Login') {
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
}

$("#recipe-search").on("submit", processForm)
// https://stackoverflow.com/questions/15195662/scroll-to-a-div-after-jquery-form-submit
$('#recipe-search').on('submit', function () {
    $('html, body').animate({
        scrollTop: $(".recipe-list").offset().top
    }, 2000);
    return false;
});