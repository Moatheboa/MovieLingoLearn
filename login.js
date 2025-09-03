const loginForm = document.getElementById("login-form");
loginForm.addEventListener("submit", function (e) {
    e.preventDefault(); // prevent default form behavior

    const username = document.getElementById("username");
    const password = document.getElementById("password");

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            "username": username.value,
            "password": password.value,
        }),
    })
        .then(res => res.text())
        .then(text => {
            if (text.includes("correct")) {
                location.href = "/";  // Relocation to lingo-page.

            } else if (text.includes("wrong")) {
                alert("Password is wrong, please try again");

            } else {
                alert("There is no user with this username.");
            }
        });
});