const members = document.getElementById("members");
const teamSize = document.getElementById("teamSize");
const teams = document.getElementById("teams");

function calculateTeams() {
    const m = parseInt(members.value);
    const t = parseInt(teamSize.value);

    if (!m || !t) return;

    teams.value = Math.ceil(m / t);
}

if (members && teamSize && teams) {
    members.addEventListener("input", calculateTeams);
    teamSize.addEventListener("input", calculateTeams);
}