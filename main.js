fetch('/getdata')
  .then(response => response.json())
  .then(data => {

    let currentImgPath = data.img_path;
    let currentEnglish = data.english;
    let currentTranslation= data.spanish_shuffled;

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
            optionButton.classList.toggle("selected-option");  // changes buttons aestetics in css
            optionButton.disabled = true;  // makes is unclickable
            userGuess.value += currentTranslation[i];  // adds the word to div for user's guess
        }
        optionsDiv.appendChild(optionButton);
    }
});
