
let btnRun = document.getElementById('btnRun');


const createElementSac = (sac , configuration , valeurs_objets , i) =>{
   
    //1 seul sac :
    console.log(sac , configuration)

    const sac_details = document.getElementsByClassName('sac-details')[0]
    const sac_details_body = document.getElementById('sac-details-body')
    

    const section = document.createElement('section')
    section.classList.add('sac-details-res');

    //creation de head de saction

    const sacHead = document.createElement('div');
    sacHead.classList.add('sac-head');
    const sacHeadText = document.createElement('p')
    const headText = document.createTextNode(`Sac n°${i}`);
    sacHeadText.appendChild(headText);
    sacHead.appendChild(sacHeadText);



    //creation de contenu de sac :
    const sacContent = document.createElement('div')
    sacContent.classList.add('sac-content');
   
    configuration.forEach(objet => { // pou chque sac
        const objetParagraph = document.createElement('p');
        
        const objText = document.createTextNode(` Objet ${objet < 10 ? '0' + objet : objet} : ${valeurs_objets[objet]} , `)

        objetParagraph.appendChild(objText);
        sacContent.appendChild(objetParagraph)
    })
    // creé le total de sac


    const sacTotal = document.createElement('div');
    sacTotal.classList.add('sac-total');
    const sacTotalText = document.createElement('p')
    const totalText = document.createTextNode(`Total : ${sac}`)
    sacTotalText.appendChild(totalText);
    sacTotal.appendChild(sacTotalText);




    section.appendChild(sacHead);
    section.appendChild(sacContent);
    section.appendChild(sacTotal);
    sac_details_body.appendChild(section);
    sac_details.appendChild(sac_details_body)
    sac_details.style.display = "block"
}



const traitement_result = (data) => {

    console.log('je suis dans le data traitement')
    // console.log(data)
    placeholderContent = document.getElementById('placeholder-content') ;
    placeholderContent.style.display = 'none'; 
    
    
    const container = document.getElementsByClassName('container')[0]
    const temps_exe = document.getElementsByClassName('execution-time')[0]
    const nombre_noeud = document.getElementsByClassName('node-count')[0]
    const table_obj = document.getElementsByClassName('sac-details')[0]
    const max_val = document.getElementsByClassName('total-value')[0]
    
    // modifier les valeur des parametre de sortie
    const executionTimeLastChild = temps_exe.lastElementChild;
    const nodeCountLastChild = nombre_noeud.lastElementChild;
    const totalValueLastChild = max_val.lastElementChild;

    console.log(data.execution_time)
    console.log(data.best_configurations)
    console.log(data.max_value)
    // Modifier la valeur du dernier enfant
    if (data.execution_time < 1) {
        executionTimeLastChild.textContent = (data.execution_time * 1000).toFixed(2) + ' milliseconds';
    } else {
        executionTimeLastChild.textContent = data.execution_time.toFixed(2) + ' seconds';
    }
    
    nodeCountLastChild.textContent = data.generated_nodes;
    totalValueLastChild.textContent = data.max_value;

    // remplire la table des objet 
    
    let configuration; // Déclarer configuration en dehors du bloc if/else

    if (data.best_configurations.length != 2) {
        configuration = data.best_configurations[0];
    } else {
        configuration = data.best_configurations;
    }

    const sac_details_body = document.getElementById('sac-details-body')
    sac_details_body.innerHTML = ''; 

    for (let i = 0; i < configuration[0].length; i++) {
        const totalValue = configuration[0][i]; // Valeur totale du sac
        const objIndices = configuration[1][i]; // Indices des objets dans le sac
    
        console.log(`Sac ${i+1}: Total Value = ${totalValue}`);
        console.log(`Objets dans le sac ${i+1}: ${objIndices}`);

        
    }

    for (let i=0 ; i<configuration[0].length;i++){
        createElementSac(configuration[0][i],configuration[1][i] , data.valeurs_objets , i);
    }
   
   
    container.style.display = "block";

    
}



btnRun.addEventListener("click" , function() {
    var algorithm = document.getElementById('algorithm').value;
    var sacs = document.getElementById('sac').value;
    var objets = document.getElementById('objet').value;
    console.log(algorithm)
    console.log(sacs)
    console.log(objets)
    console.log('please wait !!!!!')

    // Désactivez les champs d'entrée et le bouton "Run"
    algorithm.disabled = true;
    sacs .disabled = true;
    objets.disabled = true;
    btnRun.disabled = true;
    // Envoi des données à la vue Django via AJAX
    fetch('/run_algorithm/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Assurez-vous de récupérer correctement le jeton CSRF
        },
        body: JSON.stringify({
            algorithm: algorithm,
            sacs: sacs,
            objets: objets
        })
    })
    .then(response => response.json())
    .then(data => {
        // Traiter les résultats renvoyés par la vue Django
        // traitement sur les données retourner
        // console.log('data')
       
        traitement_result(data);
        // Afficher les résultats sur la page
        //reactiver les button :
        algorithm.disabled = false;
        sacs.disabled = false;
        objets.disabled = false;
        btnRun.disabled = false;
    })
    .catch(error => {
        console.error('Erreur lors de l\'exécution de l\'algorithme :', error);
        algorithm.disabled = false;
        sacs.disabled = false;
        objets.disabled = false;
        btnRun.disabled = false;
    });

});


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

