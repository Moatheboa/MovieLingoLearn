let userGuess = document.getElementById("user-answer");
let sendButton = document.getElementById("send-button");
let optionsDiv = document.getElementById("options");
let wordCount = 0;  //Nr of words user sent to userGuess
let spanishLength = 0;  // Nr of words in spanish sentence

function loadData() {
    fetch('/getdata')  // When user first go to index.html and when we redirect them there after correct guess
        .then(response => response.json())
        .then(data => {
            optionsDiv.innerText = "";

            let currentImgPath = data.img_path;
            let currentEnglish = data.english_sub;
            let currentTranslation = data.spanish_shuffled;

            let img = document.getElementById("scene");
            img.src = currentImgPath;

            let englishSentence = document.getElementById("english-subtitles");
            englishSentence.innerText = currentEnglish;
            spanishLength = currentTranslation.length;
            userGuess.value = "";  // Reset to clean from last guess words
            wordCount = 0;  // Reset from last value.

            for (let i = 0; i < spanishLength; i++) {
                let optionButton = document.createElement("button");
                optionButton.id = "b" + i;
                optionButton.className = "option-button";
                optionButton.textContent = currentTranslation[i];
                optionButton.onclick = function () {
                    optionButton.classList.toggle("selected-option");  // changes buttons aesthetics in css
                    optionButton.disabled = true;  // makes it unclickable
                    userGuess.value += currentTranslation[i];  // adds the word to div for user's guess
                    wordCount += 1;
                    sendButton.disabled = (wordCount !== spanishLength);
                }
                optionsDiv.appendChild(optionButton);
            }
        });
}

loadData();

const form = document.getElementById("guess-form");  // when user clicks Send
form.addEventListener("submit", function (e) {
    e.preventDefault(); // prevent default form behavior

    fetch("/", {  // sends to server.py to check if user guessed right or wrong
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ "user-answer": userGuess.value }),
    })
        .then(res => res.text())
        .then(text => {
            if (text.includes("congrats")) {  // User was correct and there are no more sentences in db
                alert("You completed all sentences!");
                // Here we need to reset current_id in py for db, cannot acces webpage otherwise.
            } else if (text.includes("wrong")) {  // user guessed wrong
                alert("Wrong! Try again.");
                userGuess.value = "";
                wordCount = 0;
                document.querySelectorAll(".option-button").forEach(button => {
                    button.disabled = false;
                    button.classList.remove("selected-option");
                });
            } else {
                loadData(); // user guessed right, next sentence is loaded
            }
        });
});
