let token = "";
// Fonction pour authentifier et récupérer le token JWT
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const response = await fetch("http://127.0.0.1:8000/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password })
    });
    if (response.ok) {
        const data = await response.json();
        token = data.access_token;
        alert("Connexion réussie !");
    } else {
        alert("Erreur de connexion");
    }
}
// Fonction pour envoyer les données et afficher la prédiction
async function getPrediction() {
    if (!token) return alert("Veuillez vous connecter d'abord !");
    const inputData = document.getElementById("data_input").value;
    const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ data: inputData })
    });
    const result = await response.json();
    document.getElementById("result").innerText = "Résultat : " + result.prediction;
}