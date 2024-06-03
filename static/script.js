document.addEventListener('DOMContentLoaded', function() {
    const mealInputs = document.querySelectorAll('.meal-input');
    const addMealButtons = document.querySelectorAll('.add-meal');
    const mealLists = document.querySelectorAll('.meal-list');
    const mealsInput = document.getElementById('mealsInput');
    const dietForm = document.getElementById('dietForm');

    addMealButtons.forEach((button, index) => {
        const mealInput = mealInputs[index];
        const mealList = mealLists[index];
        button.addEventListener('click', () => {
            addMeal(mealInput, mealList);
        });

        mealInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                addMeal(mealInput, mealList);
            }
        });

        mealInput.addEventListener('input', (event) => {
            showSuggestions(event, index + 1);
        });
    });

    dietForm.addEventListener('submit', () => {
        updateMealsInput();
    });

    function addMeal(mealInput, mealList) {
        const meal = mealInput.value.trim();

        if (meal === '') return;

        const li = document.createElement('li');
        li.textContent = meal;

        const delButton = document.createElement('button');
        delButton.textContent = '삭제';
        delButton.className = 'del-meal';
        delButton.addEventListener('click', () => {
            mealList.removeChild(li);
        });

        li.appendChild(delButton);
        mealList.appendChild(li);

        mealInput.value = '';
        updateMealsInput();
    }

    function updateMealsInput() {
        const allMeals = [];
        mealLists.forEach((mealList, day) => {
            const mealsForDay = [];
            mealList.querySelectorAll('li').forEach(li => {
                mealsForDay.push(li.firstChild.textContent);
            });
            allMeals.push(`Day ${day + 1}: ${mealsForDay.join(', ')}`);
        });
        mealsInput.value = allMeals.join(' | ');
    }

    function showSuggestions(event, day) {
        const query = event.target.value;
        const suggestionsBox = document.getElementById(`suggestions-${day}`);

        if (query.length > 0) {
            fetch(`/search?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsBox.innerHTML = '';
                    data.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item;
                        li.addEventListener('click', () => {
                            event.target.value = item;
                            suggestionsBox.innerHTML = '';
                        });
                        suggestionsBox.appendChild(li);
                    });
                });
        } else {
            suggestionsBox.innerHTML = '';
        }
    }
});
