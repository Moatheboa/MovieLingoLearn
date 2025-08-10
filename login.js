const loginForm = document.getElementById("login-form");
loginForm.addEventListener("submit", function (e) {
    e.preventDefault(); // prevent default form behavior

    const loginFormData = new URLSearchParams(new FormData(loginForm));  // FormData takes all names+values from form and converts into URL query string

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: loginFormData,
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