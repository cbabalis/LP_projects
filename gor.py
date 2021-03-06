
"""Simple travelling salesman problem between cities."""

from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import pdb
import os
import sys
#sys.path.append("../LP_projects")
import city_ops
import csv



def create_data_model(city_names):
    data = {}
    data['distance_matrix'] = city_ops.modify_data_for_google_or(city_names)
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def print_solution(manager, routing, solution, city_names):
    """Prints solution on console."""
    path_list = []
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = 'Route for vehicle 0:\n'
    route_distance = 0
    city_names_dict = create_city_names_dict(city_names)
    while not routing.IsEnd(index):
        plan_output += ' {} ->'.format(city_names_dict[manager.IndexToNode(index)])
        path_list.append(city_names_dict[manager.IndexToNode(index)])
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(city_names_dict[manager.IndexToNode(index)])
    print(plan_output)
    plan_output += 'Route distance: {}miles\n'.format(route_distance)
    path_list.append(city_names_dict[manager.IndexToNode(index)])
    print(path_list)
    write_results_to_csv(path_list)


def write_results_to_csv(path_list):
    path_list = [elem.strip('\n') for elem in path_list]
    with open('csv_results.csv', 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(path_list)


def create_city_names_dict(city_names):
    di = {}
    i = 0
    for c in city_names:
        di[i] = c
        i += 1
    return di

def read_cities_from_file(a_file):
    cities_list = []
    with open(a_file, 'r') as f:
        for line in f:
            curr_line = line.split(",")
            cities_list.extend(curr_line)
    return cities_list


def main():
    """Entry point of the program."""
    # Instantiate the data problem.
    city_names = read_cities_from_file(sys.argv[1])
    data = create_data_model(city_names)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(manager, routing, solution, city_names)


if __name__ == '__main__':
    main()
