// data.js — all localStorage data operations for IIPMS

// ── Default internships ──
var defaultInternships = [
    { id: 1, title: "Frontend Developer Intern", company: "TechCorp",      location: "Remote",    skills: "html, css, javascript", duration: "3 months", industry: "Technology", workType: "Remote",   stipend: "$500/month", description: "Build modern web interfaces using HTML, CSS and JavaScript." },
    { id: 2, title: "Backend Developer Intern",  company: "DevSolutions",  location: "Sydney",    skills: "python, django, sql",    duration: "3 months", industry: "Technology", workType: "On-site",  stipend: "$600/month", description: "Develop scalable REST APIs and database solutions." },
    { id: 3, title: "Data Analyst Intern",        company: "DataX",         location: "Melbourne", skills: "sql, excel, python",     duration: "6 months", industry: "Technology", workType: "Hybrid",   stipend: "$550/month", description: "Analyse large datasets and produce insight reports." },
    { id: 4, title: "UI/UX Designer Intern",      company: "DesignHub",     location: "Melbourne", skills: "html, css, figma",       duration: "3 months", industry: "Marketing",  workType: "On-site",  stipend: "$480/month", description: "Design beautiful user interfaces and conduct user research." },
    { id: 5, title: "Marketing Intern",           company: "GrowthCo",      location: "Brisbane",  skills: "excel, python, tableau", duration: "4 months", industry: "Marketing",  workType: "Hybrid",   stipend: "$450/month", description: "Support digital marketing campaigns and track analytics." },
    { id: 6, title: "Cloud Engineer Intern",      company: "CloudStack",    location: "Sydney",    skills: "aws, javascript, sql",   duration: "6 months", industry: "Technology", workType: "Remote",   stipend: "$700/month", description: "Assist in deploying and maintaining cloud infrastructure." }
];

function getAllInternships() {
    var stored = localStorage.getItem("postedInternships");
    var posted = stored ? JSON.parse(stored) : [];
    var all = [];
    for (var i = 0; i < defaultInternships.length; i++) all.push(defaultInternships[i]);
    for (var j = 0; j < posted.length; j++) all.push(posted[j]);
    return all;
}

function postNewInternship(title, company, location, duration, skills, description, employerId, industry, workType, stipend) {
    var stored = localStorage.getItem("postedInternships");
    var jobs = stored ? JSON.parse(stored) : [];
    jobs.push({
        id: Date.now(), title: title, company: company, location: location,
        duration: duration, skills: skills, description: description,
        employerId: employerId, industry: industry || "", workType: workType || "",
        stipend: stipend || "", date: new Date().toLocaleDateString()
    });
    localStorage.setItem("postedInternships", JSON.stringify(jobs));
}

function deletePostedInternship(jobId, employerId) {
    var stored = localStorage.getItem("postedInternships");
    if (!stored) return;
    var jobs = JSON.parse(stored);
    var filtered = [];
    for (var i = 0; i < jobs.length; i++) {
        if (!(jobs[i].id === jobId && jobs[i].employerId === employerId)) filtered.push(jobs[i]);
    }
    localStorage.setItem("postedInternships", JSON.stringify(filtered));
}

function getEmployerJobs(employerId) {
    var stored = localStorage.getItem("postedInternships");
    if (!stored) return [];
    var all = JSON.parse(stored);
    var mine = [];
    for (var i = 0; i < all.length; i++) {
        if (all[i].employerId === employerId) mine.push(all[i]);
    }
    return mine;
}

// ── Applications ──
function saveApplication(userId, userName, userEmail, userSkills, internshipId, internshipTitle, companyName) {
    var stored = localStorage.getItem("applications");
    var apps = stored ? JSON.parse(stored) : [];
    for (var i = 0; i < apps.length; i++) {
        if (apps[i].userId == userId && apps[i].internshipId === internshipId) {
            return "You have already applied for this internship.";
        }
    }
    apps.push({
        id: Date.now(), userId: userId, userName: userName, userEmail: userEmail,
        userSkills: userSkills, internshipId: internshipId, internshipTitle: internshipTitle,
        companyName: companyName, status: "Pending", interviewDate: "", interviewNote: "",
        studentResponse: "", officerNextStep: "", officerNote: "", date: new Date().toLocaleDateString()
    });
    localStorage.setItem("applications", JSON.stringify(apps));
    return "success";
}

function getStudentApplications(userId) {
    var stored = localStorage.getItem("applications");
    if (!stored) return [];
    var all = JSON.parse(stored);
    var mine = [];
    for (var i = 0; i < all.length; i++) {
        if (all[i].userId == userId) mine.push(all[i]);
    }
    return mine;
}

function getAllApplications() {
    var stored = localStorage.getItem("applications");
    return stored ? JSON.parse(stored) : [];
}

function updateApplicationStatus(appId, newStatus, interviewDate, interviewNote) {
    var stored = localStorage.getItem("applications");
    if (!stored) return;
    var apps = JSON.parse(stored);
    for (var i = 0; i < apps.length; i++) {
        if (apps[i].id === appId) {
            apps[i].status = newStatus;
            if (interviewDate !== "") apps[i].interviewDate = interviewDate;
            if (interviewNote !== "") apps[i].interviewNote = interviewNote;
        }
    }
    localStorage.setItem("applications", JSON.stringify(apps));
}

function studentRespondToApp(appId, response) {
    var stored = localStorage.getItem("applications");
    if (!stored) return;
    var apps = JSON.parse(stored);
    for (var i = 0; i < apps.length; i++) {
        if (apps[i].id === appId) apps[i].studentResponse = response;
    }
    localStorage.setItem("applications", JSON.stringify(apps));
}

function officerSetNextStep(appId, nextStep, officerNote) {
    var stored = localStorage.getItem("applications");
    if (!stored) return;
    var apps = JSON.parse(stored);
    for (var i = 0; i < apps.length; i++) {
        if (apps[i].id === appId) {
            apps[i].officerNextStep = nextStep;
            apps[i].officerNote = officerNote;
        }
    }
    localStorage.setItem("applications", JSON.stringify(apps));
}

// ── Notifications ──
function sendNotification(toUserId, fromName, subject, message) {
    var stored = localStorage.getItem("notifications");
    var notes = stored ? JSON.parse(stored) : [];
    notes.push({
        id: Date.now(), toUserId: toUserId, fromName: fromName,
        subject: subject, message: message,
        date: new Date().toLocaleDateString(), isRead: false
    });
    localStorage.setItem("notifications", JSON.stringify(notes));
}

function getNotificationsForUser(userId) {
    var stored = localStorage.getItem("notifications");
    if (!stored) return [];
    var all = JSON.parse(stored);
    var mine = [];
    for (var i = 0; i < all.length; i++) {
        if (all[i].toUserId == userId) mine.push(all[i]);
    }
    return mine;
}

function markNotificationRead(noteId) {
    var stored = localStorage.getItem("notifications");
    if (!stored) return;
    var notes = JSON.parse(stored);
    for (var i = 0; i < notes.length; i++) {
        if (notes[i].id === noteId) notes[i].isRead = true;
    }
    localStorage.setItem("notifications", JSON.stringify(notes));
}

function deleteNotification(noteId) {
    var stored = localStorage.getItem("notifications");
    if (!stored) return;
    var notes = JSON.parse(stored);
    var kept = [];
    for (var i = 0; i < notes.length; i++) {
        if (notes[i].id !== noteId) kept.push(notes[i]);
    }
    localStorage.setItem("notifications", JSON.stringify(kept));
}

// ── Weekly Logs ──
function saveWeeklyLog(userId, userName, companyName, weekNumber, hoursWorked, tasks, challenges, reflection) {
    var stored = localStorage.getItem("weeklyLogs");
    var logs = stored ? JSON.parse(stored) : [];
    logs.push({
        id: Date.now(), userId: userId, userName: userName, companyName: companyName || "",
        weekNumber: weekNumber, hoursWorked: hoursWorked, tasks: tasks,
        challenges: challenges, reflection: reflection, date: new Date().toLocaleDateString()
    });
    localStorage.setItem("weeklyLogs", JSON.stringify(logs));
}

function getStudentLogs(userId) {
    var stored = localStorage.getItem("weeklyLogs");
    if (!stored) return [];
    var all = JSON.parse(stored);
    var mine = [];
    for (var i = 0; i < all.length; i++) {
        if (all[i].userId == userId) mine.push(all[i]);
    }
    return mine;
}

function getCompanyLogs(companyName) {
    var stored = localStorage.getItem("weeklyLogs");
    if (!stored) return [];
    var all = JSON.parse(stored);
    var res = [];
    for (var i = 0; i < all.length; i++) {
        if (all[i].companyName && all[i].companyName.toLowerCase() === companyName.toLowerCase()) res.push(all[i]);
    }
    return res;
}

function getAllWeeklyLogs() {
    var stored = localStorage.getItem("weeklyLogs");
    return stored ? JSON.parse(stored) : [];
}

// ── Progress Entries (Officer tracking) ──
function saveProgressEntry(studentName, internship, stage, notes) {
    var stored = localStorage.getItem("progressEntries");
    var entries = stored ? JSON.parse(stored) : [];
    entries.push({
        id: Date.now(), studentName: studentName, internship: internship,
        stage: stage, notes: notes, date: new Date().toLocaleDateString()
    });
    localStorage.setItem("progressEntries", JSON.stringify(entries));
}

function getAllProgressEntries() {
    var stored = localStorage.getItem("progressEntries");
    return stored ? JSON.parse(stored) : [];
}

// ── Evaluations ──
function saveEvaluation(fromUserId, fromName, fromRole, studentId, studentName, internshipTitle, ratings, comments, recommendation) {
    var stored = localStorage.getItem("evaluations");
    var evals = stored ? JSON.parse(stored) : [];
    evals.push({
        id: Date.now(), fromUserId: fromUserId, fromName: fromName, fromRole: fromRole,
        studentId: studentId, studentName: studentName, internshipTitle: internshipTitle,
        ratings: ratings, comments: comments, recommendation: recommendation,
        date: new Date().toLocaleDateString()
    });
    localStorage.setItem("evaluations", JSON.stringify(evals));
}

function getStudentEvaluations(studentId) {
    var stored = localStorage.getItem("evaluations");
    if (!stored) return [];
    var all = JSON.parse(stored);
    var mine = [];
    for (var i = 0; i < all.length; i++) {
        if (all[i].studentId == studentId) mine.push(all[i]);
    }
    return mine;
}

function getAllEvaluations() {
    var stored = localStorage.getItem("evaluations");
    return stored ? JSON.parse(stored) : [];
}

// ── Offers ──
function saveOffer(employerId, employerName, studentId, studentName, internshipTitle, startDate, endDate, stipend, terms) {
    var stored = localStorage.getItem("offers");
    var offers = stored ? JSON.parse(stored) : [];
    offers.push({
        id: Date.now(), employerId: employerId, employerName: employerName,
        studentId: studentId, studentName: studentName, internshipTitle: internshipTitle,
        startDate: startDate, endDate: endDate, stipend: stipend, terms: terms,
        status: "Pending Officer Approval", officerApproved: false,
        date: new Date().toLocaleDateString()
    });
    localStorage.setItem("offers", JSON.stringify(offers));
}

function getStudentOffers(studentId) {
    var stored = localStorage.getItem("offers");
    if (!stored) return [];
    var all = JSON.parse(stored);
    var mine = [];
    for (var i = 0; i < all.length; i++) {
        if (all[i].studentId == studentId) mine.push(all[i]);
    }
    return mine;
}

function getEmployerOffers(employerId) {
    var stored = localStorage.getItem("offers");
    if (!stored) return [];
    var all = JSON.parse(stored);
    var mine = [];
    for (var i = 0; i < all.length; i++) {
        if (all[i].employerId == employerId) mine.push(all[i]);
    }
    return mine;
}

function getAllOffers() {
    var stored = localStorage.getItem("offers");
    return stored ? JSON.parse(stored) : [];
}

function updateOfferStatus(offerId, newStatus, officerApproved) {
    var stored = localStorage.getItem("offers");
    if (!stored) return;
    var offers = JSON.parse(stored);
    for (var i = 0; i < offers.length; i++) {
        if (offers[i].id === offerId) {
            offers[i].status = newStatus;
            if (officerApproved !== undefined) offers[i].officerApproved = officerApproved;
        }
    }
    localStorage.setItem("offers", JSON.stringify(offers));
}

// ── Employer Verification ──
function saveVerificationRequest(employerId, employerName, companyName, industry, website, abn) {
    var stored = localStorage.getItem("verificationRequests");
    var reqs = stored ? JSON.parse(stored) : [];
    for (var i = 0; i < reqs.length; i++) {
        if (reqs[i].employerId === employerId) return "You have already submitted a verification request.";
    }
    reqs.push({
        id: Date.now(), employerId: employerId, employerName: employerName,
        companyName: companyName, industry: industry, website: website, abn: abn,
        status: "Pending", date: new Date().toLocaleDateString()
    });
    localStorage.setItem("verificationRequests", JSON.stringify(reqs));
    return "success";
}

function getAllVerificationRequests() {
    var stored = localStorage.getItem("verificationRequests");
    return stored ? JSON.parse(stored) : [];
}

function updateVerificationStatus(reqId, newStatus, employerId) {
    var stored = localStorage.getItem("verificationRequests");
    if (!stored) return;
    var reqs = JSON.parse(stored);
    for (var i = 0; i < reqs.length; i++) {
        if (reqs[i].id === reqId) reqs[i].status = newStatus;
    }
    localStorage.setItem("verificationRequests", JSON.stringify(reqs));
    if (newStatus === "Approved") {
        var users = JSON.parse(localStorage.getItem("users")) || [];
        for (var j = 0; j < users.length; j++) {
            if (users[j].id == employerId) users[j].verified = true;
        }
        localStorage.setItem("users", JSON.stringify(users));
    }
}

// ── Supervisor Assignments ──
function getSupervisorStudents(supervisorId) {
    var stored = localStorage.getItem("supervisorAssignments");
    if (!stored) return [];
    var all = JSON.parse(stored);
    var mine = [];
    for (var i = 0; i < all.length; i++) {
        if (all[i].supervisorId == supervisorId) mine.push(all[i]);
    }
    return mine;
}

function assignStudentToSupervisor(supervisorId, supervisorName, studentId, studentName) {
    var stored = localStorage.getItem("supervisorAssignments");
    var list = stored ? JSON.parse(stored) : [];
    for (var i = 0; i < list.length; i++) {
        if (list[i].supervisorId == supervisorId && list[i].studentId == studentId) return;
    }
    list.push({
        id: Date.now(), supervisorId: supervisorId, supervisorName: supervisorName,
        studentId: studentId, studentName: studentName, date: new Date().toLocaleDateString()
    });
    localStorage.setItem("supervisorAssignments", JSON.stringify(list));
}

// ── Completion Records ──
function saveCompletion(studentId, studentName, internshipTitle, companyName, startDate, endDate, grade, notes) {
    var stored = localStorage.getItem("completions");
    var list = stored ? JSON.parse(stored) : [];
    list.push({
        id: Date.now(), studentId: studentId, studentName: studentName,
        internshipTitle: internshipTitle, companyName: companyName,
        startDate: startDate, endDate: endDate, grade: grade, notes: notes,
        date: new Date().toLocaleDateString()
    });
    localStorage.setItem("completions", JSON.stringify(list));
}

function getAllCompletions() {
    var stored = localStorage.getItem("completions");
    return stored ? JSON.parse(stored) : [];
}

// ── Skill Match Score (simple, used on internships page) ──
function getMatchScore(studentSkills, jobSkills) {
    if (!studentSkills || !jobSkills) return 0;
    var studentList = studentSkills.toLowerCase().split(",");
    var jobList     = jobSkills.toLowerCase().split(",");
    var matchCount  = 0;
    for (var i = 0; i < jobList.length; i++) {
        var jobSkill = jobList[i].trim();
        for (var j = 0; j < studentList.length; j++) {
            if (studentList[j].trim() === jobSkill && jobSkill !== "") matchCount++;
        }
    }
    if (jobList.length === 0) return 0;
    return Math.round((matchCount / jobList.length) * 100);
}

// ── Full Match Result (used on matches page — multi-factor scoring) ──
function getFullMatchResult(user, job) {
    var score   = 0;
    var reasons = [];

    // 1) Skill match — up to 60 points
    var skillScore = 0;
    if (user.skills && user.skills !== "" && job.skills && job.skills !== "") {
        skillScore = getMatchScore(user.skills, job.skills);
        var pts = Math.round(skillScore * 0.6);
        score += pts;

        var studentList = user.skills.toLowerCase().split(",");
        var jobList     = job.skills.toLowerCase().split(",");
        var matched = [];
        for (var i = 0; i < jobList.length; i++) {
            var js = jobList[i].trim();
            for (var j = 0; j < studentList.length; j++) {
                if (studentList[j].trim() === js && js !== "") {
                    matched.push(js);
                }
            }
        }
        if (matched.length > 0) {
            reasons.push("Skills matched: " + matched.join(", ") + " (" + skillScore + "% overlap, +" + pts + " pts)");
        } else {
            reasons.push("No skill overlap with this role (" + skillScore + "% match)");
        }
    } else {
        reasons.push("No skills on your profile — add skills to improve your score");
    }

    // 2) Industry preference — up to 20 points
    if (user.industryPref && user.industryPref !== "" && job.industry && job.industry !== "") {
        if (user.industryPref.toLowerCase() === job.industry.toLowerCase() || user.industryPref === "Any") {
            score += 20;
            reasons.push("Industry match: " + job.industry + " (+20 pts)");
        } else {
            reasons.push("Industry mismatch: you prefer " + user.industryPref + ", this role is " + job.industry);
        }
    }

    // 3) Work type preference — up to 10 points
    if (user.workType && user.workType !== "" && job.workType && job.workType !== "") {
        if (user.workType === "Any" || user.workType.toLowerCase() === job.workType.toLowerCase()) {
            score += 10;
            reasons.push("Work type match: " + job.workType + " (+10 pts)");
        }
    }

    // 4) Location preference — up to 10 points
    if (user.locationPref && user.locationPref !== "" && job.location && job.location !== "") {
        var locPref = user.locationPref.toLowerCase();
        var jobLoc  = job.location.toLowerCase();
        if (locPref.indexOf(jobLoc) !== -1 || jobLoc.indexOf(locPref) !== -1 ||
            jobLoc === "remote" || locPref === "remote" || locPref === "any") {
            score += 10;
            reasons.push("Location compatible: " + job.location + " (+10 pts)");
        }
    }

    if (score > 100) score = 100;
    if (reasons.length === 0) reasons.push("Complete your profile to get personalised match reasons.");

    return { score: score, reasons: reasons };
}
