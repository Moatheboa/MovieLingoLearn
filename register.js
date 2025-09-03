const regForm = document.getElementById("reg-form");
regForm.addEventListener("submit", function (e) {
    e.preventDefault(); // prevent default form behavior

    const regUsername = document.getElementById("reg-username");
    const regPassword = document.getElementById("reg-password");

    fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "regUsername": regUsername.value,
            "regPassword": regPassword.value,
        }),
    })
        .then(res => res.text())
        .then(text => {
            if (text.includes("success")) {
                alert("Your account is created!");
                location.href = "login.html";  // Relocation to login page after alert.

            } else if (text.includes("user exists")) {  // username already in use
                alert("Username already exists, please try another.");

            } else {  // Exception in DBHandler
                alert("Unknown problem, couldn't add user to database.");
            }
        });
});
