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
import random
from queue import PriorityQueue

import numpy as np
import copy

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
        print('dans run config',best_configurations)
        print('length',len(best_configurations))
        print('max_val dans_config',max_value)
        
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
        generated_nodes = 0
        N = 4
        MaxGen = 10
        best_configurations, max_value = knapsack_genetic_algorithm(N, MaxGen, items, knapsacks_capacity)
        # Initialisez des listes pour stocker les valeurs et le contenu des sacs
        values_in_sacks = []
        contents_of_sacks = []

        # Parcourez chaque sac dans les meilleures configurations
        for sack_content in best_configurations:
            # Calculez la valeur totale du sac en utilisant les indices des objets
            sack_value = sum([objets[i].value_obj for i in sack_content])
            values_in_sacks.append(sack_value)
            contents_of_sacks.append(sack_content)

        return max_value, (values_in_sacks, contents_of_sacks), generated_nodes, valeurs_objets 
    
    elif(algo=='BSO'):
        generated_nodes = 0
        Sref = generate_solution_BSO(items, knapsacks_capacity)  
        sref_eva = evaluate_solution_BSO(Sref, items, knapsacks_capacity)
        nbees = 5
        MaxIter = 7
        LS_MaxIter = 2
        MaxChances = 3
        
        last_solution, tabouList = BSO(MaxIter, nbees, LS_MaxIter, Sref, items, knapsacks_capacity, MaxChances)

        sorted_tabouList = sorted(tabouList, key=lambda x: evaluate_solution_BSO(x[0], items, knapsacks_capacity), reverse=True)
        best_configurations = sorted_tabouList[0][0]
        # Getting the evaluation of the best solution in tabouList
        max_value = evaluate_solution_BSO( best_configurations, items, knapsacks_capacity)
        print("Best Tabou Solution:", sorted_tabouList[0][0], "==>", max_value )
        
        values_in_sacks = []
        contents_of_sacks = []

        # Parcourez chaque sac dans les meilleures configurations
        for sack_content in best_configurations:
            # Calculez la valeur totale du sac en utilisant les indices des objets
            sack_value = sum([objets[i].value_obj for i in sack_content])
            values_in_sacks.append(sack_value)
            contents_of_sacks.append(sack_content)

        print (max_value, (values_in_sacks, contents_of_sacks))
        return max_value, (values_in_sacks, contents_of_sacks), generated_nodes, valeurs_objets 




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





# /////////////////////////////////////Genitic////////////////////////////////////



def generate_solution(items, knapsacks_capacity, population_size, exploration_rate=0.5):
    population = []
    for _ in range(population_size):
        solution = [[] for _ in range(len(knapsacks_capacity))]
        remaining_capacity = knapsacks_capacity.copy()
        allocated_items = set()  # Garder trace des objets déja alloué

        # Mettre aléatoirement les objets dans les sacs 
        for item_index, item in enumerate(items):
            knapsack_index = random.randint(0, len(knapsacks_capacity) - 1)
            if random.random() < exploration_rate and remaining_capacity[knapsack_index] >= item[0] and item_index not in allocated_items:
                solution[knapsack_index].append(item_index)
                remaining_capacity[knapsack_index] -= item[0]
                allocated_items.add(item_index)  # Mark item as allocated
        
        # Mettre les objets restant (si possible) dans les sacs (ceux qui n'ont pas été choisi lors de la distribution aléatoire) 
        for item_index, item in enumerate(items):
            if item_index not in allocated_items:
                #Trouver le sac avec la plus grande capacité restante
                best_knapsack = max(range(len(remaining_capacity)), key=lambda k: remaining_capacity[k])
                if remaining_capacity[best_knapsack] >= item[0]:
                    solution[best_knapsack].append(item_index)
                    remaining_capacity[best_knapsack] -= item[0]
                    allocated_items.add(item_index)  # Mark item as allocated
        
        # Vérifier que le poids total du sac ne dépasse pas sa capacité
        for knapsack_index, knapsack_items in enumerate(solution):
            knapsack_weight = sum(items[item_index][0] for item_index in knapsack_items)
            if knapsack_weight > knapsacks_capacity[knapsack_index]:
                # Si le poids dépasse la capacité, retirer des objets jusqu'a la satisfaction de la condition
                while knapsack_weight > knapsacks_capacity[knapsack_index]:
                    # Retirer le dérnier item ajouté au sac
                    item_index_to_remove = solution[knapsack_index].pop()
                    # mettre à jour la capacité restante
                    remaining_capacity[knapsack_index] += items[item_index_to_remove][0]
                    allocated_items.remove(item_index_to_remove)
                    # Mettre à jour le poids du sac
                    knapsack_weight -= items[item_index_to_remove][0]
        
        population.append(solution)
        # print(solution,"\n")
    
    return population


def evaluate_solution(solution, items, knapsacks_capacity):
    knapsacks_value = [0] * len(knapsacks_capacity)
    for i, knapsack in enumerate(solution):
        for item_index in knapsack:
            knapsacks_value[i] += items[item_index][1] 
    return sum(knapsacks_value)




def tournament_knapsack_selection(population, evaluations, tournament_size):
    selected_pairs = []
    remaining_indices = list(range(len(population)))
    
    #Répeter la selection par tournoi jusqu'a l'obtention du nombre de parents souhaité
    while len(selected_pairs) < len(population) // 2:
        # Choisir aléatoirement des individus pour le tournoi
        participants_indices = random.sample(remaining_indices, tournament_size)
        
        # Evaluer les participant et choisir les 2 meilleurs comme parents
        sorted_participants = sorted(participants_indices, key=lambda idx: evaluations[idx], reverse=True)
        parent1, parent2 = population[sorted_participants[0]], population[sorted_participants[1]]
        selected_pairs.append((parent1, parent2))
        # print(parent1, "\t", parent2, "\n")
        #Retirer les individus sélectionnée de l'ensemble des participant potentiels
        remaining_indices = [idx for idx in remaining_indices if idx not in participants_indices]
    
    return selected_pairs






# def knapsack_mutation(solution, knapsacks_capacity, items):
#     mutated_solution = solution.copy()
#     kps_capacity = knapsacks_capacity.copy()

#     knapsacks_weight = [sum(items[item_index][0] for item_index in knapsack) for knapsack in mutated_solution]

#     for i in range(len(kps_capacity)):
#         kps_capacity[i] -= knapsacks_weight[i]

#     # Choisir aléatoirement 2 sacs pour permuter leurs objets
#     knapsack_index1, knapsack_index2 = random.sample(range(len(solution)), 2)
    
#     # vérifier que les 2 sacs contiennent des objets et si la permutation est possible (la capacité n'est pas dépassée)
#     if mutated_solution[knapsack_index1] and mutated_solution[knapsack_index2]:
#         # choix du sac aléatoire
#         item_index1 = random.choice(range(len(mutated_solution[knapsack_index1])))
#         item_index2 = random.choice(range(len(mutated_solution[knapsack_index2])))
        
#         item_to_swap1 = mutated_solution[knapsack_index1][item_index1]
#         item_to_swap2 = mutated_solution[knapsack_index2][item_index2]
        
#         # Vérifier que la permutation est valide
#         if (kps_capacity[knapsack_index1] + items[item_to_swap1][0] - items[item_to_swap2][0] >= 0 and
#             kps_capacity[knapsack_index2] + items[item_to_swap2][0] - items[item_to_swap1][0] >= 0):
#             # Mettre à jour la capacité des sacs
#             kps_capacity[knapsack_index1] += items[item_to_swap2][0] - items[item_to_swap1][0]
#             kps_capacity[knapsack_index2] += items[item_to_swap1][0] - items[item_to_swap2][0]
#             # Permuter les objets
#             mutated_solution[knapsack_index1][item_index1] = item_to_swap2
#             mutated_solution[knapsack_index2][item_index2] = item_to_swap1

            
#     # print(mutated_solution,"\n")
#     return mutated_solution



def knapsack_mutation(solution, knapsacks_capacity, items):
    mutated_solution = solution.copy()
    kps_capacity = knapsacks_capacity.copy()

    knapsacks_weight = [sum(items[item_index][0] for item_index in knapsack) for knapsack in mutated_solution]

    for i in range(len(kps_capacity)):
        kps_capacity[i] -= knapsacks_weight[i]

    # Le nombre des permutations echouée
    unsuccessful_attempts = 0

    #Réessayer une autre permutation
    while unsuccessful_attempts < 12:

        # Choisir aléatoirement 2 sacs pour permuter leurs objets
        knapsack_index1, knapsack_index2 = random.sample(range(len(solution)), 2)
        
        # vérifier que les 2 sacs contiennent des objets et si la permutation est possible (la capacité n'est pas dépassée)
        if mutated_solution[knapsack_index1] and mutated_solution[knapsack_index2]:
            # choix du sac aléatoire
            item_index1 = random.choice(range(len(mutated_solution[knapsack_index1])))
            item_index2 = random.choice(range(len(mutated_solution[knapsack_index2])))
            
            item_to_swap1 = mutated_solution[knapsack_index1][item_index1]
            item_to_swap2 = mutated_solution[knapsack_index2][item_index2]
            
            # Vérifier que la permutation est valide
            if (kps_capacity[knapsack_index1] + items[item_to_swap1][0] - items[item_to_swap2][0] >= 0 and
                kps_capacity[knapsack_index2] + items[item_to_swap2][0] - items[item_to_swap1][0] >= 0):
                # Mettre à jour la capacité des sacs
                kps_capacity[knapsack_index1] += items[item_to_swap2][0] - items[item_to_swap1][0]
                kps_capacity[knapsack_index2] += items[item_to_swap1][0] - items[item_to_swap2][0]
                # Permuter les objets
                mutated_solution[knapsack_index1][item_index1] = item_to_swap2
                mutated_solution[knapsack_index2][item_index2] = item_to_swap1
                break  # permutation possible => Sortir de la boucle

        # Incrémenter le compteur du nombre de permutations echouées
        unsuccessful_attempts += 1

            
    print(mutated_solution,"\n")
    return mutated_solution







def knapsack_crossover(parent1, parent2):
    num_knapsacks = min(len(parent1), len(parent2))
    child1 = [[] for _ in range(num_knapsacks)]
    child2 = [[] for _ in range(num_knapsacks)]
    
    # Appliquer le croisement pour chaque sac
    crossover_point = random.randint(0, num_knapsacks - 1)
    
    # Garder trace des objets inclus dans les sacs des enfants
    items_in_child1 = set()
    items_in_child2 = set()
    
    for i in range(num_knapsacks):
        if i < crossover_point:
            # Ajouter un sac du parent1 à l'enfant 1 et un sac du parent 2 au fils 2 
            for item in parent1[i]:
                if item not in items_in_child1:
                    child1[i].append(item)
                    items_in_child1.add(item)
            for item in parent2[i]:
                if item not in items_in_child2:
                    child2[i].append(item)
                    items_in_child2.add(item)
        else:
            # Ajouter un sac du parent2 à l'enfant 1 et du parent1 à l'enfant2
            for item in parent2[i]:
                if item not in items_in_child1:
                    child1[i].append(item)
                    items_in_child1.add(item)
            for item in parent1[i]:
                if item not in items_in_child2:
                    child2[i].append(item)
                    items_in_child2.add(item)
    
    # print(child1, "\t", child2, "\n")
    children = []
    children.append(child1)
    children.append(child2)
    return children


def knapsack_replacement(population, evaluations, children_crossover, evaluations_crossover, children_mutation, evaluations_mutation):
    # Rassembler les enfants et leurs évaluations

    children = children_crossover + children_mutation
    children_evaluations = evaluations_crossover + evaluations_mutation
    
    # Combiner les parents et les enfants
    combined_population = list(zip(population, evaluations)) + list(zip(children, children_evaluations))
    
    # Trier les individus
    combined_population.sort(key=lambda x: x[1], reverse=True)
    # print("combined_population : ", combined_population, "\n")
    # Sélectionner les meilleurs individus 
    new_population = [ind for ind, _ in combined_population[:len(population)]]
    
    return new_population

def best_solution(population, evaluations):
    best_solution = None
    best_fitness = float('-inf') 

    for solution, fitness in zip(population, evaluations):
        if fitness > best_fitness:
            best_solution = solution
            best_fitness = fitness
    
    return best_solution, best_fitness


def knapsack_genetic_algorithm(N, MaxGen, items, knapsacks_capacity):
    # Initialiser la population aléatoirement
    # print("Population : \n")
    pop = generate_solution(items, knapsacks_capacity, N)

    # Evaluations de la population initiale
    evaluations = [evaluate_solution(solution, items, knapsacks_capacity) for solution in pop]
    # print("evaluations :", evaluations)
    # print()
    
    for _ in range(MaxGen):
        # Selection des parents
        # print("Parents : \n")
        parents = tournament_knapsack_selection(pop, evaluations, 2)


        # Croisement
        # print("children_crossover : \n")
        children_crossover = [knapsack_crossover(parents[i][0], parents[i][1]) for i in range(len(parents))]

        flattened_children = []
        for child_pair in children_crossover:
            for child in child_pair:
                flattened_children.append(child)
        
        children_crossover = flattened_children
        
        # Mutation
        # print("children_mutation : \n")
        children_mutation = [knapsack_mutation(child, knapsacks_capacity, items) for child in children_crossover]

        # Evaluation des enfants
        evaluations_crossover = [evaluate_solution(child, items, knapsacks_capacity) for child in children_crossover]
        # print("evaluations_crossover : ",evaluations_crossover,"\n")
        evaluations_mutation = [evaluate_solution(child, items, knapsacks_capacity) for child in children_mutation]
        # print("evaluations_mutation : ",evaluations_mutation,"\n")

        # Replacement dans la population
        pop = knapsack_replacement(pop, evaluations, children_crossover, evaluations_crossover, children_mutation, evaluations_mutation)
        # print("pop : ", pop, "\n")
        evaluations = [evaluate_solution(solution, items, knapsacks_capacity) for solution in pop]
        # print("evaluations : ", evaluations, "\n")
    
    # Retourner le meilleur individu
    return best_solution(pop, evaluations)




# /////////////////////////////////BSO///////////////////////////////




def generate_solution_BSO(items, knapsacks_capacity, exploration_rate=0.5):
    solution = [[] for _ in range(len(knapsacks_capacity))] #Initialisation des sacs vides

    remaining_capacity = knapsacks_capacity.copy()
    allocated_items = set()  # garder trace des objets déja placés

    # Placer les objets dans les sacs aléatoirement
    for item_index, item in enumerate(items):
        knapsack_index = random.randint(0, len(knapsacks_capacity) - 1)
        if random.random() < exploration_rate and remaining_capacity[knapsack_index] >= item[0] and item_index not in allocated_items:
            solution[knapsack_index].append(item_index)
            remaining_capacity[knapsack_index] -= item[0]
            allocated_items.add(item_index) 
    
    # Placer les objets restants
    for item_index, item in enumerate(items):
        if item_index not in allocated_items:
            # Trouver le sac avec la capacité restante la plus elevée
            best_knapsack = max(range(len(remaining_capacity)), key=lambda k: remaining_capacity[k])
            if remaining_capacity[best_knapsack] >= item[0]:
                solution[best_knapsack].append(item_index)
                remaining_capacity[best_knapsack] -= item[0]
                allocated_items.add(item_index)  
    
    # Vérifier si le poids total d'un des sac dépasse la capacité de ce dérnier 
    for knapsack_index, knapsack_items in enumerate(solution):
        knapsack_weight = sum(items[item_index][0] for item_index in knapsack_items)
        if knapsack_weight > knapsacks_capacity[knapsack_index]:
            # S'il c'est le cas, retirer des objets du sac jusqu'a ce que la le poids soit vérifé
            while knapsack_weight > knapsacks_capacity[knapsack_index]:
                # Retirer le dernier objet ajouté au sac
                item_index_to_remove = solution[knapsack_index].pop()
                # recalculer et mettre à jour la capacité restante
                remaining_capacity[knapsack_index] += items[item_index_to_remove][0]
                allocated_items.remove(item_index_to_remove)
                # mettre à jour le poids du sac
                knapsack_weight -= items[item_index_to_remove][0]
    
    return solution


def evaluate_solution_BSO(solution, items, knapsacks_capacity):

    knapsacks_value = [0] * len(knapsacks_capacity)
    for i, knapsack in enumerate(solution):
        for item_index in knapsack:
            knapsacks_value[i] += items[item_index][1]  
    return sum(knapsacks_value)





def generateBees(Sref, nbees, items, capacities, flip):
    solutions = []
    solution = [knapsack[:] for knapsack in Sref]  # Initialiser la 1ere solution avec Sref
    
    for y in range(nbees):
        s = solution.copy()
        solutions.append(copy.deepcopy(s))

        # garder trace des objets déja placés dans les sacs
        placed_items = set(item for knapsack in s for item in knapsack)

        # Pour chaque sac dans Sref
        for knapsack_index, knapsack in enumerate(s):
            f = flip
            remaining_items = set(range(len(items))) - placed_items  # Récupérer les objets qui n'ont été mis dans aucun sac

            # Si le sac est vide, essayer de mettre des objets restants
            if not knapsack:
                for item_index in sorted(remaining_items):
                    item_weight = items[item_index][0]
                    if item_weight <= capacities[knapsack_index]:  # Vérifier si l'objet peut tenir dans le sac
                        s[knapsack_index].append(item_index)
                        placed_items.add(item_index)
                        remaining_items.remove(item_index)
                        f -= 1
                        if f == 0:
                            break

            # Pour chaque objet dans le sac courant
            for item_index in knapsack:
                remaining_items_list = list(remaining_items)  # mettre les items restant sous format de liste

                # Parcourir les objets restant 
                for i in range(len(remaining_items_list)):
                    new_item_index = remaining_items_list[i]

                    # Calculer le nouveau poids du sac si les 2 items sont permutés
                    knapsack_weight = sum(items[i][0] for i in solution[knapsack_index])
                    new_item_weight = items[new_item_index][0]

                    # Si le nouveau poids ne depasse pas la capacité du sac
                    if (knapsack_weight - items[item_index][0] + new_item_weight) <= capacities[knapsack_index]:
                        # Remplacer l'objet courant avec le nouveau
                        f -= 1
                        s[knapsack_index].remove(item_index)
                        s[knapsack_index].append(new_item_index)
                        placed_items.remove(item_index)  # Retirer l'item courant de la liste des items placés
                        placed_items.add(new_item_index)  # Le remplacer avec le nouvel objet

                        remaining_items.remove(new_item_index)
                        remaining_items.add(item_index)

                        item_index = new_item_index
                        if f == 0:
                            break

    return solutions


def localSearch(solution, LS_MaxIter, items, capacities):
    best_solution = solution[:]
    best_fitness = evaluate_solution_BSO(solution, items, capacities)
    best_solutions = [best_solution]  # Liste pour sauvegarder les solutions avec les meilleurs fitness
    
    for _ in range(LS_MaxIter):
        for knapsack_index1, knapsack1 in enumerate(solution):
            for knapsack_index2, knapsack2 in enumerate(solution):
                if knapsack_index1 != knapsack_index2 and knapsack1 and knapsack2:
                    for item_index1 in knapsack1:
                        for item_index2 in knapsack2:
                            # Echnager les objets entre les sacs
                            neighbor = [knapsack[:] for knapsack in solution]
                            neighbor[knapsack_index1].remove(item_index1)
                            neighbor[knapsack_index2].remove(item_index2)
                            neighbor[knapsack_index1].append(item_index2)
                            neighbor[knapsack_index2].append(item_index1)
                            
                            # Vérifier la contrainte de la capacité
                            if (
                                sum(items[item_index][0] for item_index in neighbor[knapsack_index1]) <= capacities[knapsack_index1]
                                and sum(items[item_index][0] for item_index in neighbor[knapsack_index2]) <= capacities[knapsack_index2]
                            ):
                                # Evaluer la nouvelle solution
                                neighbor_fitness = evaluate_solution_BSO(neighbor, items, capacities)
                                # Mettre à jour la meilleure solution
                                if neighbor_fitness > best_fitness:
                                    best_solution = neighbor[:]
                                    best_fitness = neighbor_fitness
                                    if best_solution not in best_solutions:
                                        best_solutions = [best_solution] 
                                elif neighbor_fitness == best_fitness:
                                    if neighbor not in best_solutions:
                                        best_solutions.append(neighbor[:])

    print("Best_solutions : ")
    for sol in best_solutions:
        # Print the inner list
        print(sol)
    print()
    return best_solutions



def update(DanceTable, Bees, items, capacities):
    for bee in Bees:
        DanceTable.append((evaluate_solution_BSO(bee, items, capacities), bee))
    return DanceTable





def calculate_diversity(solution1, solution2):
    diversity = 0
    for knapsacks1, knapsacks2 in zip(solution1, solution2):
        if len(knapsacks1) == 1 and len(knapsacks2) == 1:
            diversity += 1 if knapsacks1[0] != knapsacks2[0] else 0 #Si les sacs ne contiennent qu'un seul objet et qu'ils sont différents +1
        else:
            diversity += len(set(knapsacks1) ^ set(knapsacks2)) 
            #len(set(knapsacks1) ^ set(knapsacks2))  : retourne le nombre d'éléments qui sont présents dans l'un des ensembles 
            #knapsacks1 ou knapsacks2, mais pas dans les deux ensembles simultanément.
    return diversity


def bestDiversity(DanceTable, Sbest):
    best_diversity = float('-inf')
    best_solution = Sbest[1]

    for _, solution in DanceTable:
        diversity = calculate_diversity(solution, best_solution)
        if diversity > best_diversity:
            best_diversity = diversity
            best_solution = solution

    return best_solution




def getBest(Sbest, Sref, tabouList, MaxChances, DanceTable ,items, capacities):
    
    NbChances = None
    for _ , (solution, nb_chances) in enumerate(tabouList):
            if solution == Sbest[1]:
                NbChances =  nb_chances
                break

    if NbChances is None:  # Si la solution n'est pas dans la liste tabou
        NbChances = MaxChances

    Delta_f = Sbest[0] - evaluate_solution_BSO(Sref, items, capacities)

    if Delta_f > 0:
        Sref = Sbest[1]
        if NbChances < MaxChances:
            NbChances = MaxChances
    else:
        if NbChances > 0:
            NbChances -= 1
            Sref = max(DanceTable, key=lambda x: x[0])[1]  # Choisir la meilleur solution en terme de fitness
        else:
            Sref = bestDiversity(DanceTable, Sbest)  # choisir la meilleur solution en terme de diversité 
            print("Sbest : ", Sbest, "==> BestDiversity :", Sref)
            NbChances = MaxChances
    return Sref, NbChances


def BSO(MaxIter, nbees, LS_MaxIter, Sref, items, capacities, MaxChances):
    DanceTable = []
    tabouList = [(Sref[:], MaxChances)]  # Initialiser la liste tabou avec Sref
    NbChances = MaxChances

    for _ in range(MaxIter):

        print("Tabou List : ")
        for tb in tabouList:
            print(tb)
        print()
        
        Bees = generateBees(Sref, nbees, items, capacities, 2)
        print("Bees : ")
        for b in Bees:
            print(b)
        print()

        Bees_list = []  # 
        for i, bee in enumerate(Bees):
            Ls_bees = localSearch(bee, LS_MaxIter, items, capacities)
            Bees_list.extend(Ls_bees) 
        Bees.extend(Bees_list) 

        DanceTable = update(DanceTable, Bees, items, capacities)
        DanceTable.sort(key=lambda x: x[0], reverse=True)

        Sbest = DanceTable[0]
        Sref, NbChances = getBest(Sbest, Sref, tabouList , MaxChances, DanceTable , items, capacities)

        found = False
        for i, (solution, nb_chances) in enumerate(tabouList):
            if solution == Sref:
                tabouList[i] = (solution, NbChances)
                found = True
                break
        if not found:
            tabouList.append((Sref[:],NbChances)) 


        
    return Sref, tabouList