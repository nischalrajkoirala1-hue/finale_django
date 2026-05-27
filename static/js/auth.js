// auth.js — handles register, login, logout, session

function registerUser(firstName, lastName, email, role, password, confirmPassword, extraData) {
    if (!firstName || !lastName || !email || !role || !password) {
        return "Please fill in all required fields.";
    }
    if (password !== confirmPassword) {
        return "Passwords do not match.";
    }
    if (password.length < 6) {
        return "Password must be at least 6 characters.";
    }
    var users = JSON.parse(localStorage.getItem("users")) || [];
    for (var i = 0; i < users.length; i++) {
        if (users[i].email.toLowerCase() === email.toLowerCase()) {
            return "An account with this email already exists.";
        }
    }
    var ex = extraData || {};
    var newUser = {
        id: Date.now(), firstName: firstName, lastName: lastName,
        email: email.toLowerCase(), role: role, password: password,
        photo: ex.photo || "", skills: ex.skills || "",
        company: ex.company || "", industry: ex.industry || "",
        website: ex.website || "", abn: ex.abn || "",
        course: ex.course || "", wam: ex.wam || "",
        availability: ex.availability || "", industryPref: ex.industryPref || "",
        workType: ex.workType || "", locationPref: ex.locationPref || "",
        university: ex.university || "", department: ex.department || "",
        cvData: ex.cvData || "", verified: false
    };
    users.push(newUser);
    localStorage.setItem("users", JSON.stringify(users));
    return "success";
}

function loginUser(email, password) {
    var users = JSON.parse(localStorage.getItem("users")) || [];
    for (var i = 0; i < users.length; i++) {
        if (users[i].email.toLowerCase() === email.toLowerCase() && users[i].password === password) {
            sessionStorage.setItem("loggedInUser", JSON.stringify(users[i]));
            return "success";
        }
    }
    return "Invalid email or password. Please try again.";
}

function getLoggedInUser() {
    var raw = sessionStorage.getItem("loggedInUser");
    if (!raw) return null;
    return JSON.parse(raw);
}

function requireRole(role) {
    var user = getLoggedInUser();
    if (!user) { window.location.href = "login.html"; return null; }
    if (user.role !== role) { window.location.href = "login.html"; return null; }
    return user;
}

function updateUserSkills(newSkills) {
    var user = getLoggedInUser();
    if (!user) return;
    user.skills = newSkills;
    sessionStorage.setItem("loggedInUser", JSON.stringify(user));
    var users = JSON.parse(localStorage.getItem("users")) || [];
    for (var i = 0; i < users.length; i++) {
        if (users[i].id === user.id) users[i].skills = newSkills;
    }
    localStorage.setItem("users", JSON.stringify(users));
}

function updateUserProfile(fields) {
    var user = getLoggedInUser();
    if (!user) return;
    for (var key in fields) { if (fields.hasOwnProperty(key)) user[key] = fields[key]; }
    sessionStorage.setItem("loggedInUser", JSON.stringify(user));
    var users = JSON.parse(localStorage.getItem("users")) || [];
    for (var i = 0; i < users.length; i++) {
        if (users[i].id === user.id) {
            for (var k in fields) { if (fields.hasOwnProperty(k)) users[i][k] = fields[k]; }
        }
    }
    localStorage.setItem("users", JSON.stringify(users));
}

function logoutUser() {
    sessionStorage.removeItem("loggedInUser");
    window.location.href = "index.html";
}
