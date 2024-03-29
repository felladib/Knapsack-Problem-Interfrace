"""_summary_
    MKP_env/Scripts/activate
    cd MKP_interface
    python manage.py runserver
"""
from django.shortcuts import render
from .models import objet, sacados
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
import time
from collections import deque
from queue import PriorityQueue

def home(request):
     objets = objet.objects.all()
     sacs = sacados.objects.all()
    
     # Passer les objets et les sacs récupérés au template
     context = {'objets': objets, 'sacs': sacs}

     
     return render(request, "home.html" , context)
 
 

 
def simulation(request):
     return render(request , "Simulation.html")
     
 
 



def delete_sac(request, sac_id):
    sac = get_object_or_404(sacados , ids_ac =sac_id)
    sac.delete()
    return redirect('homepage')


def delete_obj(request, obj_id):
    obj = get_object_or_404(objet , id_obj = obj_id)
    obj.delete()
    return redirect('homepage')


def add_sac(request):
    print("////////////// numero de sac :////////////////::" )
    if request.method == 'POST':
        data = json.loads(request.body)
        numerosac = data.get('numerosac')
        valeursac = data.get('valeursac')
        print(f"//////////numero de sac{numerosac}///// capacity {valeursac}/////////")
        # Vérifiez si les valeurs sont valides
        if numerosac is not None and valeursac is not None:
            # Créer une nouvelle instance de modèle et l'enregistrer dans la base de données
            new_sac = sacados(ids_ac=numerosac, capacity_sac=valeursac)
            new_sac.save()
            return JsonResponse({'message': 'Le sac a été ajouté avec succès'})
        else:
            return JsonResponse({'error': 'Les données du formulaire sont incomplètes'}, status=400)
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)



def add_obj(request):
  
    if request.method == 'POST':
        data = json.loads(request.body)
        numeroobj = data.get('numeroobj')
        valeurobj = data.get('valeurobj')
        poidobj = data.get('poidobj')
        
        
        # Vérifiez si les valeurs sont valides
        if numeroobj is not None and valeurobj is not None:
            # Créer une nouvelle instance de modèle et l'enregistrer dans la base de données
            new_obj= objet(id_obj=numeroobj, poid_obj=poidobj ,value_obj= valeurobj  )
            new_obj.save()
            return JsonResponse({'message': 'Le sac a été ajouté avec succès'})
        else:
            return JsonResponse({'error': 'Les données du formulaire sont incomplètes'}, status=400)
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


def run(request):
    
    if request.method == 'POST':
        data = json.loads(request.body)
        algo = data.get('algorithm')
        nb_sac = int(data.get('sacs'))
        nb_obj= int(data.get('objets'))
        start_time = time.time()
        
        max_value, best_configurations, generated_nodes , valeurs_objets = execute_Algo(algo ,nb_sac , nb_obj)
        end_time = time.time()
            
        
        execution_time = (end_time - start_time)
        
        response_data = {
            'max_value': max_value,
            'best_configurations': best_configurations,
            'generated_nodes': generated_nodes,
            'execution_time': execution_time,
            'valeurs_objets' :valeurs_objets,
            'message': 'L\'algorithme a été exécuté avec succès'
        }
        
        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    
    
def execute_Algo(algo ,nb_sac , nb_obj):
    sacs = sacados.objects.all()[:nb_sac]  # Récupère les nb_sac premiers sacs
    objets = objet.objects.all()[:nb_obj]  # Récupère les nb_obj premiers objets
    valeurs_objets = [obj.value_obj for obj in objets]
   
    items = [(objet.poid_obj, objet.value_obj) for objet in objets] #convertir vers tuple (poid,value)
    knapsacks_capacity = [sac.capacity_sac for sac in sacs]
    knapsacks_weight = [0 for sac in sacs]
    
    if (algo == 'dfs'):
        max_value, best_configurations, generated_nodes = knapsack_DFS(items, knapsacks_capacity, knapsacks_weight)
        return max_value, best_configurations, generated_nodes , valeurs_objets
    elif (algo == 'bfs'):
        max_value, best_configurations, generated_nodes = knapsack_BFS(items, knapsacks_capacity, knapsacks_weight)
        return max_value, best_configurations, generated_nodes , valeurs_objets
    elif (algo == 'astar'):
        max_value, best_configurations, generated_nodes = knapsack_A_star(items, knapsacks_capacity, knapsacks_weight)
        return max_value, best_configurations, generated_nodes , valeurs_objets
    elif (algo == 'genetic'):
        return None
   
   
    # print(max_value, best_configurations, generated_nodes)
    
# def DFS(nb_sac , nb_obj):
   
#     sacs = sacados.objects.all()[:nb_sac]  # Récupère les nb_sac premiers sacs
#     objets = objet.objects.all()[:nb_obj]  # Récupère les nb_obj premiers objets
#     valeurs_objets = [obj.value_obj for obj in objets]
   
#     items = [(objet.poid_obj, objet.value_obj) for objet in objets] #convertir vers tuple (poid,value)
#     knapsacks_capacity = [sac.capacity_sac for sac in sacs]
#     knapsacks_weight = [0 for sac in sacs]
   
#     max_value, best_configurations, generated_nodes = knapsack_DFS(items, knapsacks_capacity, knapsacks_weight)
#     return max_value, best_configurations, generated_nodes , valeurs_objets
#     # print(max_value, best_configurations, generated_nodes)
   
    
    
    
    
    
def knapsack_DFS(items, knapsacks_capacity, knapsacks_weight):
    # Fonction DFS
    def dfs(items, knapsacks_capacity, knapsacks_weight, knapsacks_value, current_item_index, selected_items):
        nonlocal max_value, best_configurations, generated_nodes
        
        # Incrémenter le compteur de nœuds générés à chaque appel de la fonction DFS
        generated_nodes += 1

        # Cas de base : Si tous les items ont été considérés Ou bien si la capacité de tous les sacs à été épuisée
        if current_item_index == len(items): #Le dérnier objet
            total_value = sum(knapsacks_value) #La valeur de tous les sacs combinés
            if total_value > max_value:
                max_value = total_value
                best_configurations.clear()
                best_configurations.append((knapsacks_value.copy(), [items[:] for items in selected_items]))
            elif total_value == max_value:
                best_configurations.append((knapsacks_value.copy(), [items[:] for items in selected_items]))
            return

        # sinon
        item_weight, item_value = items[current_item_index]

        # Essayer de mettre l'item dans chacun des sacs
        for knapsack_index in range(len(knapsacks_capacity)): #Itérer sur les sacs
            if knapsacks_capacity[knapsack_index] >= item_weight:
                #Si l'objet peut être mis dans le sac alors
                knapsacks_capacity[knapsack_index] -= item_weight #Diminuer la capacité du sac
                knapsacks_weight[knapsack_index] += item_weight #Augmenter le poids du sac
                knapsacks_value[knapsack_index] += item_value #Augmenter la valeur du sac
                selected_items[knapsack_index].append(current_item_index) #Ajouter l'objet au objets selectionnés

                # Appel récursif pour l'objet suivant
                # print(selected_items)
                dfs(items, knapsacks_capacity, knapsacks_weight, knapsacks_value, current_item_index + 1, selected_items)
                
                # Retour arrière pour essayer d'autre combinaisons 
                # Enlever l'objet du sac
                knapsacks_capacity[knapsack_index] += item_weight
                knapsacks_weight[knapsack_index] -= item_weight
                knapsacks_value[knapsack_index] -= item_value
                selected_items[knapsack_index].pop()
            # else: print("item",current_item_index,"not possible in", knapsack_index)

        # Passer à l'objet suivant pour le cas où l'objet courant n'a été mis dans aucun des sacs
        # print("item ",current_item_index,"in none of the bags ",selected_items, "\n")
        dfs(items, knapsacks_capacity, knapsacks_weight, knapsacks_value, current_item_index + 1, selected_items)

    max_value = float('-inf')
    best_configurations = []
    generated_nodes = 0

    # Initialiser les sacs
    knapsacks_value = [0] * len(knapsacks_capacity) #La valeur initiale du sac
    selected_items = [[] for _ in range(len(knapsacks_capacity))]  # Liste de listes pour sauvegarder les objets selectionnés pour chaque sac, initialement vide

    # Premier appel  (avec 0 étant le 1er objet)
    dfs(items, knapsacks_capacity, knapsacks_weight, knapsacks_value, 0, selected_items)

    return max_value, best_configurations, generated_nodes




    


def knapsack_BFS(items, knapsacks_capacity, knapsacks_weight):
    # Elements de la file : (items_index, knapsacks_capacity, knapsacks_weight, knapsacks_value, selected_items)
    queue = deque([(0, knapsacks_capacity[:], knapsacks_weight[:], [0] * len(knapsacks_capacity), [[] for _ in range(len(knapsacks_capacity))])])
    
    max_value = float('-inf')
    best_configuration = []
    generated_nodes = 0  # Initialiser le compteur de nœuds générés

    while queue: #Tant qu'il y a encore des objets 
        generated_nodes += 1
        current_item_index, knapsacks_capacity, knapsacks_weight, knapsacks_value, selected_items = queue.popleft() #Défiler 

        if current_item_index == len(items): #
            total_value = sum(knapsacks_value)
            if total_value > max_value: #Comparer la valeur de la solution actuelle par rapport à la meilleur solution
                max_value = total_value
                best_configuration = [(knapsacks_value.copy(), [items[:] for items in selected_items])]
            elif total_value == max_value: #si la solution actuelle est égale à la meilleur solution l'ajouter à la liste de meilleurs solutions
                best_configuration.append((knapsacks_value.copy(), [items[:] for items in selected_items]))
            continue

        item_weight, item_value = items[current_item_index] #initialiser item_weight, item_value avec le poids et la valeur de l'item courant

        for knapsack_index in range(len(knapsacks_capacity)): #parcourir les sacs
            if knapsacks_capacity[knapsack_index] >= item_weight :
                #Si l'objet peut être mis dans le sac alors
                new_capacity = knapsacks_capacity[:]
                new_capacity[knapsack_index] -= item_weight #Diminuer la capacité du sac

                new_weight = knapsacks_weight[:]
                new_weight[knapsack_index] += item_weight #Augmenter le poids du sac

                new_value = knapsacks_value[:]
                new_value[knapsack_index] += item_value #Augmenter la valeur du sac

                new_selected_items = [items[:] for items in selected_items]
                new_selected_items[knapsack_index].append(current_item_index) #Ajouter l'item à la liste des items du sac

                # print(new_selected_items)
                queue.append((current_item_index + 1, new_capacity, new_weight, new_value, new_selected_items)) #Enfiler l'item suivant

            # else: print("item",current_item_index,"not possible in", knapsack_index)
        
        #Enfiler l'item suivant pour le cas où l'item courant n'a été mis dans aucun des sacs
        queue.append((current_item_index + 1, knapsacks_capacity[:], knapsacks_weight[:], knapsacks_value[:], [items[:] for items in selected_items]))
        # print("item",current_item_index,"in none of the bags",selected_items,"\n")

    return max_value, best_configuration, generated_nodes



# //////////////////////////////////////////////////////ASTAR////////////////////////////////////

def heuristic(knapsacks_capacity, items, current_item_index):
    # Estime la valeur patentielle des objets restants 

    remaining_value = 0 #Contient la valeur totale des objets restant
    #Itérer sur les objets restant à partir de l'index de l'objet courrant
    for item_weight, item_value in items[current_item_index:]:

        #Vérifier si l'objet peut être mis dans le sac (poids_obj < capacité restante du sac)
        if item_weight <= knapsacks_capacity:
            remaining_value += item_value# Ajouter la valeur de l'objet
            knapsacks_capacity -= item_weight # Réduire la capacité du sac
        else:
            # Si le poids de l'objet est supérieur à la capacité du sac
            # Calculer une valeur partielle sur la base de la capacité restance 
            # et l'ajouter à la valeur restante
            remaining_value += knapsacks_capacity * (item_value / item_weight)
            break #break, car les autres éléments ne peuvent pas être entièrement placés

    return remaining_value


def knapsack_A_star(items, knapsacks_capacity, knapsacks_weight):
    queue = PriorityQueue()

    #Elements de la queue : (priority = g+h , current_item_index, knapsacks_capacity, knapsacks_weight, valeur, selected_items)
    queue.put((0, 0, knapsacks_capacity[:], knapsacks_weight[:], [0] * len(knapsacks_capacity), [[] for _ in range(len(knapsacks_capacity))]))

    max_value = float('-inf')
    best_configuration = []
    generated_nodes = 0

    while not queue.empty(): #Tant qu'il y a encore des objets
        generated_nodes += 1
        _, current_item_index, knapsacks_capacity, knapsacks_weight, knapsacks_value, selected_items = queue.get()

        if current_item_index == len(items): #Si tous les objets ont été parcouru
            total_value = sum(knapsacks_value) 
            if total_value > max_value:
                max_value = total_value
                print("max_val =",max_value,"\n")
                best_configuration = [(knapsacks_value.copy(), [items[:] for items in selected_items])]
            elif total_value == max_value:
                best_configuration.append((knapsacks_value.copy(), [items[:] for items in selected_items])) 
            return max_value, best_configuration, generated_nodes

        item_weight, item_value = items[current_item_index]
        
        for knapsack_index in range(len(knapsacks_capacity)):
            if knapsacks_capacity[knapsack_index] >= item_weight:
               #Si l'objet peut être mis dans le sac alors
                new_capacity = knapsacks_capacity[:]
                new_capacity[knapsack_index] -= item_weight

                new_weight = knapsacks_weight[:]
                new_weight[knapsack_index] += item_weight

                new_value = knapsacks_value[:]
                new_value[knapsack_index] += item_value

                new_selected_items = [items[:] for items in selected_items]
                new_selected_items[knapsack_index].append(current_item_index)

                priority = -(sum(new_value) + heuristic(new_capacity[knapsack_index], items, current_item_index + 1)) 
                #Négatif car la PriorityQueue donne la priorité aux éléments ayant les plus petites valeurs

                # print(new_selected_items,"-> g :",sum(new_value) ,"-> f :", - priority)
                queue.put((priority, current_item_index + 1, new_capacity, new_weight, new_value, new_selected_items))

            # else: print("item",current_item_index,"not possible in", knapsack_index, "capacity = ", knapsacks_capacity[knapsack_index] - item_weight)

        p = - sum(knapsacks_value[:])
        queue.put((0, current_item_index + 1, knapsacks_capacity[:], knapsacks_weight[:], knapsacks_value[:], [items[:] for items in selected_items]))
        # print("item",current_item_index,"in none of the bags",selected_items," p=",- p,"\n")
        
    return max_value, best_configuration, generated_nodes

def Genetic(nb_sac , nb_obj):
     return 0, 0, 0