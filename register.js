const regForm = document.getElementById("reg-form");
regForm.addEventListener("submit", function (e) {
    e.preventDefault(); // prevent default form behavior

    const regFormData = new URLSearchParams(new FormData(regForm));  // FormData takes all names+values from form and converts into URL query string

    fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: regFormData,
    })
        .then(res => res.text())
        .then(text => {
            if (text.includes("success")) {
                console.log("account created");
                alert("Your account is created!");
                location.href = "login.html";  // Relocation to login page after alert.

            } else if (text.includes("user exists")) {  // username already in use
                console.log("user exists");
                alert("Username already exists, please try another.");

            } else {
                console.log("invalid password");
                alert("Some problem, try again with another username and/or password.");
            }
        });
});
