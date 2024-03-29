var openModalBtn = document.getElementById("openModalBtn"); // retourner le button add
var modal = document.getElementById("myModal"); // le model 
console.log(modal);
// Récupérer la référence des boutons "Ajouter" et "Annuler"
var addBtn = document.getElementById("addBtn");
var cancelBtn = document.getElementById("cancelBtn");

// Récupérer la référence du span de fermeture de la fenêtre modale
var closeSpan = document.getElementsByClassName("close")[0];

// Lorsque l'utilisateur clique sur le bouton "Ajouter", afficher la fenêtre modale
openModalBtn.onclick = function() {
  modal.style.display = "block";
}

// Lorsque l'utilisateur clique sur le bouton "Annuler" ou sur le span de fermeture, masquer la fenêtre modale
cancelBtn.onclick = function() {
  modal.style.display = "none";
}

closeSpan.onclick = function() {
  modal.style.display = "none";
}


addBtn.onclick = function() {
  var numeroobj = document.getElementById("numero").value;
  var poidobj = document.getElementById("poids").value;
  var valeurobj = document.getElementById("valeur").value;


  console.log(numeroobj)
  console.log(valeurobj)
  // Envoyer les données au serveur via une requête POST
  fetch('/add_obj/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')  // Récupérer le jeton CSRF
      },
      body: JSON.stringify({ numeroobj: numeroobj, valeurobj: valeurobj , poidobj : poidobj })
  })
  .then(response => {
      if (response.ok) {
          // Recharger la page ou effectuer d'autres actions nécessaires
          window.location.reload();
      } else {
          // Gérer les erreurs en cas de réponse incorrecte du serveur
          console.error('Erreur lors de l\'ajout du sac');
      }
  })
  .catch(error => {
      console.error('Erreur de réseau:', error);
  });
};

// Lorsque l'utilisateur clique en dehors de la fenêtre modale, masquer la fenêtre modale
window.onclick = function(event) {
  console.log('avant delete modal');
  if (event.target == modal) {
    console.log('fin de add');
    modal.style.display = "none";
  }
}








// Vous pouvez ajouter ici la logique pour ajouter l'objet lorsque l'utilisateur clique sur le bouton "Ajouter"

////2eme add button sac 
var openModalBtnsac = document.getElementById("openModalBtnsac"); // retourner le button add
console.log(openModalBtnsac)
var modalsac = document.getElementById("myModalsac"); // le model 

// Récupérer la référence des boutons "Ajouter" et "Annuler"
var addBtnsac = document.getElementById("addBtnSac");
var cancelBtnsac = document.getElementById("cancelBtnSac");

// Récupérer la référence du span de fermeture de la fenêtre modale
var closeSpansac = document.getElementsByClassName("closesac")[0];

// Lorsque l'utilisateur clique sur le bouton "Ajouter", afficher la fenêtre modale
openModalBtnsac.onclick = function() {
  console.log('hela');
  modalsac.style.display = "block";
}

// Lorsque l'utilisateur clique sur le bouton "Annuler" ou sur le span de fermeture, masquer la fenêtre modale
cancelBtnsac.onclick = function() {
  modalsac.style.display = "none";
}

closeSpansac.onclick = function() {
  modalsac.style.display = "none";
}

// Lorsque l'utilisateur clique en dehors de la fenêtre modale, masquer la fenêtre modale
window.onclick = function(event) {
  if (event.target == modalsac) {
    modalsac.style.display = "none";
  }
}
addBtnsac.onclick = function() {
  var numerosac = document.getElementById("numerosac").value;
  var valeursac = document.getElementById("valeursac").value;

  console.log(numerosac)
  console.log(valeursac)
  // Envoyer les données au serveur via une requête POST
  fetch('/add_sac/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')  // Récupérer le jeton CSRF
      },
      body: JSON.stringify({ numerosac: numerosac, valeursac: valeursac })
  })
  .then(response => {
      if (response.ok) {
          // Recharger la page ou effectuer d'autres actions nécessaires
          window.location.reload();
      } else {
          // Gérer les erreurs en cas de réponse incorrecte du serveur
          console.error('Erreur lors de l\'ajout du sac');
      }
  })
  .catch(error => {
      console.error('Erreur de réseau:', error);
  });
};

// Fonction pour récupérer le jeton CSRF
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}