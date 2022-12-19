import numpy as np

H = 240 # l'horizon de temps en minutes.

'''
Retourne la matrice contenue dans file_matrix
'''
def read_matrix(file_matrix):
    with open(file_matrix, 'r') as f:
        lines = [[int(n) for n in line.strip().split(' ')] for line in f]
    M = np.array([np.array(xi) for xi in lines])
    return M

'''
Lit le probleme et renvoie le nombre de portes, de stations, de vehicule.
Il renvoie aussi une liste de requetes . 
'''
def read_problem(filename):
    instance_file = open(filename, 'r')
    lines_file = instance_file.readlines()
     
    nb_doors = int(lines_file[0])
    nb_stops = int(lines_file[1])
    nb_vehicles, capacity = [int(s) for s in lines_file[2].split(' ')]
    nbRequests = int(lines_file[3])
    requests = []
    for l in range(4, nbRequests+4):
        requests.append([int(s) for s in lines_file[l].split(' ')])
    return nb_doors, nb_stops, requests, nb_vehicles, capacity


'''
Retourne la solution. Les arguments retounes sont des listes de la taille du nombre de requetes
    - req_use_transfer: 1 si la requete utilise un transfert; sinon 0
    - req_station_indices: paire des stations avant et apres le transfert. -1 si pas de transfert
    - req_time_doors: paire des temps aux pickup et delivery points
    - req_time_stations: paire des temps aux stations. -1 si pas de transfert
    - req_vehicles_used: paire de vehicule qui prennent en charge la requete. un seul vehicule si pas de transfert
'''
def read_solution(filename):
    instance_file = open(filename, 'r')
    lines_file = instance_file.readlines()
    
    req_use_transfer = []
    req_station_indices = []
    req_time_doors = []
    req_time_stations = []
    req_vehicles_used = []
    
    nb_requests = int(lines_file[0])
    for i in np.arange(1,nb_requests*2,2):
        use_transfer = int(lines_file[i])
        req_use_transfer.append(use_transfer)
        if use_transfer == 1:
            # _b correspond a "before" et _a a "after". c'est assez contre-intuitif, mais j'aime bien cette notation
            t_p_b, v_b, t_d_b, s_b, s_a, t_p_a, v_a, t_d_a = [int(s) for s in lines_file[i+1].split(' ')]
            req_station_indices.append([s_b, s_a])
            req_time_doors.append([t_p_b, t_d_a])
            req_time_stations.append([t_d_b, t_p_a])
            req_vehicles_used.append([v_b, v_a])
        else: 
            t_p, v, t_d = [int(s) for s in lines_file[i+1].split(' ')]
            req_station_indices.append(-1)
            req_time_doors.append([t_p, t_d])
            req_time_stations.append(-1)
            req_vehicles_used.append(v)
    return req_use_transfer, req_station_indices, req_time_doors, req_time_stations, req_vehicles_used

'''
vehicle_time vecteur de temps
time_to_insert int qui correspond a un temps
retoune l'indice ou time_to_insert doit etre inserer dans vehicle_time
'''
def get_index_to_insert(vehicle_time, time_to_insert):
    list_index_smaller_than_time = np.where(vehicle_time < time_to_insert)[0]
    if len(list_index_smaller_than_time) == 0:
        return 0
    else:
        return max(list_index_smaller_than_time)+1
    

def insert_in_vehicle_vectors(vehicle_indices_door, index_door, vehicle_indices_station, index_station, vehicle_index_pickup, 
                              index_request_at_pickup, vehicle_index_delivery, index_request_at_delivery, vehicle_time, time, index_to_insert):
    vehicle_indices_door = np.insert(vehicle_indices_door, index_to_insert, index_door)
    vehicle_indices_station = np.insert(vehicle_indices_station, index_to_insert, index_station)
    vehicle_index_pickup = np.insert(vehicle_index_pickup, index_to_insert, index_request_at_pickup)
    vehicle_index_delivery = np.insert(vehicle_index_delivery, index_to_insert, index_request_at_delivery)
    vehicle_time = np.insert(vehicle_time, index_to_insert, time)
    return vehicle_indices_door, vehicle_indices_station, vehicle_index_pickup, vehicle_index_delivery, vehicle_time
    
def insert_depot_in_route(vehicle_indices_door, vehicle_indices_station, vehicle_index_pickup, 
                           vehicle_index_delivery, vehicle_time, M_dd, M_ds):
    # We insert at the beginning
    if(vehicle_indices_door[0] != -1):
        # The vehicle starts by going to a door
        vehicle_time = np.insert(vehicle_time, 0, vehicle_time[0]-M_dd[0][vehicle_indices_door[0]])
    else:
        # The vehicle starts by going to a station
        vehicle_time = np.insert(vehicle_time, 0, vehicle_time[0]-M_ds[0][vehicle_indices_station[0]])
    vehicle_indices_door = np.insert(vehicle_indices_door, 0, 0)
    vehicle_indices_station = np.insert(vehicle_indices_station, 0, -1)
    vehicle_index_pickup = np.insert(vehicle_index_pickup, 0, -1)
    vehicle_index_delivery = np.insert(vehicle_index_delivery, 0, -1)
    
    # We nsert et the end
    if(vehicle_indices_door[-1] != -1):
        # The vehicle ends by going to a door
        vehicle_time = np.insert(vehicle_time, len(vehicle_time), vehicle_time[-1]+M_dd[vehicle_indices_door[-1]][0])
    else:
        # The vehicle ends by going to a station
        vehicle_time = np.insert(vehicle_time, len(vehicle_time), vehicle_time[-1]+M_ds[0][vehicle_indices_station[-1]])
    vehicle_indices_door = np.insert(vehicle_indices_door, len(vehicle_indices_door), 0)
    vehicle_indices_station = np.insert(vehicle_indices_station, len(vehicle_indices_station), -1)
    vehicle_index_pickup = np.insert(vehicle_index_pickup, len(vehicle_index_pickup), -1)
    vehicle_index_delivery = np.insert(vehicle_index_delivery, len(vehicle_index_delivery), -1)
    return vehicle_indices_door, vehicle_indices_station, vehicle_index_pickup, vehicle_index_delivery, vehicle_time

def insert_depot_in_routes(vehicle_indices_door, vehicle_indices_station, vehicle_index_pickup, 
                           vehicle_index_delivery, vehicle_time, M_dd, M_ds):
    for i in range(len(vehicle_indices_door)):
        vehicle_indices_door[i], vehicle_indices_station[i], vehicle_index_pickup[i], vehicle_index_delivery[i], vehicle_time[i] = insert_depot_in_route(vehicle_indices_door[i], vehicle_indices_station[i], vehicle_index_pickup[i], 
                           vehicle_index_delivery[i], vehicle_time[i], M_dd, M_ds)
 
'''
Transforme une solutions de requetes en routes. Retourne des liste de liste de routes, ou chaque
sous-liste correspond a un vehicule/route. Toutes les sous-listes du meme vehicule ont la meme taille,
qui correspond au nombres de points visites.
vehicle_indices_door: L'indice de la porte visitee. 0 = depot. -1 si on ne vistite pas une porte (station)
vehicle_indices_station: L'indice de la station visitee. -1 si on ne vistite pas une station (depot ou porte)
vehicle_index_pickup: L'indice de la requete qu'on prend . -1 si on ne prend aucune requete (depot ou depose une requete)
vehicle_index_delivery: L'indice de la requete qu'on depose . -1 si on ne depose aucune requete (depot ou prend une requete)
vehicle_time: Les temps correspondant aux actions.
'''    
def transform_requests_solution_to_routes(nb_vehicles, requests, req_use_transfer, req_station_indices, req_time_doors, req_time_stations, req_vehicles_used):
    vehicle_indices_door = []
    vehicle_indices_station = []
    vehicle_index_pickup = []
    vehicle_index_delivery = []
    vehicle_time = []
    for i in range(nb_vehicles):
        vehicle_indices_door.append(np.array([], dtype=int))
        vehicle_indices_station.append(np.array([], dtype=int))
        vehicle_index_pickup.append(np.array([], dtype=int))
        vehicle_index_delivery.append(np.array([], dtype=int))
        vehicle_time.append(np.array([], dtype=int))

    nb_requests = len(requests)
    for i in range(nb_requests):
        # We insert pickup point at door
        if(req_use_transfer[i]):
            v = req_vehicles_used[i][0]
        else:
            v = req_vehicles_used[i]
        index_to_insert = get_index_to_insert(vehicle_time[v], req_time_doors[i][0])
        vehicle_indices_door[v], vehicle_indices_station[v], vehicle_index_pickup[v], vehicle_index_delivery[v], vehicle_time[v] = insert_in_vehicle_vectors(vehicle_indices_door[v], requests[i][0], vehicle_indices_station[v], -1, vehicle_index_pickup[v], 
                                  i, vehicle_index_delivery[v], -1, vehicle_time[v], req_time_doors[i][0], index_to_insert)
        # We insert the delivery point
        if(req_use_transfer[i]):
            v = req_vehicles_used[i][1]
        else:
            v = req_vehicles_used[i]
        index_to_insert = get_index_to_insert(vehicle_time[v], req_time_doors[i][1])
        vehicle_indices_door[v], vehicle_indices_station[v], vehicle_index_pickup[v], vehicle_index_delivery[v], vehicle_time[v] = insert_in_vehicle_vectors(vehicle_indices_door[v], requests[i][3], vehicle_indices_station[v], -1, vehicle_index_pickup[v], 
                                  -1, vehicle_index_delivery[v], i, vehicle_time[v], req_time_doors[i][1], index_to_insert)
        # We insert the sations
        if(req_use_transfer[i]):
            # before the transfer
            v = req_vehicles_used[i][0]
            index_to_insert = get_index_to_insert(vehicle_time[v], req_time_stations[i][0])
            vehicle_indices_door[v], vehicle_indices_station[v], vehicle_index_pickup[v], vehicle_index_delivery[v], vehicle_time[v] = insert_in_vehicle_vectors(vehicle_indices_door[v], -1, vehicle_indices_station[v], req_station_indices[i][0], vehicle_index_pickup[v], 
                                  -1, vehicle_index_delivery[v], i, vehicle_time[v], req_time_stations[i][0], index_to_insert)

            # after the transfer
            v = req_vehicles_used[i][1]
            index_to_insert = get_index_to_insert(vehicle_time[v], req_time_stations[i][1])
            vehicle_indices_door[v], vehicle_indices_station[v], vehicle_index_pickup[v], vehicle_index_delivery[v], vehicle_time[v] = insert_in_vehicle_vectors(vehicle_indices_door[v], -1, vehicle_indices_station[v], req_station_indices[i][1], vehicle_index_pickup[v], 
                                  i, vehicle_index_delivery[v], -1, vehicle_time[v], req_time_stations[i][1], index_to_insert)
    return vehicle_indices_door, vehicle_indices_station, vehicle_index_pickup, vehicle_index_delivery, vehicle_time

M_door_door = read_matrix('M_door_door.txt')
M_door_station = read_matrix('M_door_station.txt')
M_station_station = read_matrix('M_station_station.txt')
M_tram = read_matrix('M_tram.txt')

n = 'LH_1_1'
nb_doors, nb_stops, requests, nb_vehicles, capacity = read_problem('instance/'+n+'.txt')
req_use_transfer, req_station_indices, req_time_doors, req_time_stations, req_vehicles_used = read_solution('solution/'+n+'.txt')
vehicle_indices_door, vehicle_indices_station, vehicle_index_pickup, vehicle_index_delivery, vehicle_time = transform_requests_solution_to_routes(nb_vehicles, requests, req_use_transfer, req_station_indices, req_time_doors, req_time_stations, req_vehicles_used)
insert_depot_in_routes(vehicle_indices_door, vehicle_indices_station, vehicle_index_pickup, vehicle_index_delivery, vehicle_time, M_door_door, M_door_station)









