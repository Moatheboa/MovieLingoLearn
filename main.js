let currentImgPath = "content/01_breaking_bad/images/1.jpg";
let currentEnglish = "This should be fetched from server";
let currentTranslation= ["Esto ", "obtenido ", "ser ", "debo ", "server", "del "]; // Already divided in parts and randomly shuffled

let img = document.getElementById("scene");
img.src = currentImgPath;

let englishSentence = document.getElementById("english-subtitles");
englishSentence.innerText = currentEnglish;

let userGuess = document.getElementById("user-answer");

let optionsDiv = document.getElementById("options");

for (let i = 0; i < currentTranslation.length; i++ ) {
    let optionButton = document.createElement("button");
    optionButton.id = "b" + i;
    optionButton.className = "option-button";
    optionButton.textContent = currentTranslation[i];
    optionButton.onclick = function() {
        optionButton.classList.toggle("selected-option");
        userGuess.value += currentTranslation[i];
        console.log("Clicked on " + optionButton.textContent);
    }
    optionsDiv.appendChild(optionButton);
}