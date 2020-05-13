"""Vehicles Routing Problem (VRP)."""

from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from scipy.spatial import distance
import matplotlib.pyplot as plt
import pdb
import time
import json


def create_equal_distance():
    data = {}
    points_matrix = create_grid_points()
    data['distance_matrix'] = calculate_grid_distances(points_matrix)
    data['num_vehicles'] = 4
    data['depot'] = 0
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
    with open('data.json') as json_file:
        data = json.load(json_file)
    return data


def create_grid_points():
    points_matrix = []
    for i in range(0,8):
        for j in range(0, 8):
            points_matrix.append((i, j))
    print("points matrix just above!\n")
    return points_matrix

def calculate_grid_distances(points_matrix):
    distance_matrix = []
    row_matrix = []
    for point_a in points_matrix:
        for point_b in points_matrix:
            dst = distance.euclidean(point_a, point_b)
            row_matrix.append(dst)
        distance_matrix.append(row_matrix)
        row_matrix = []
    #print(distance_matrix)
    #print("distance matrix just above!\n")
    return distance_matrix


def get_vrp_nodes_path(data, manager, routing, solution):
    """ This method gets the paths for all nodes."""
    all_paths = {}
    for vehicle_id in range(data['num_vehicles']):
        all_paths[vehicle_id] = return_nodes(manager, routing, solution, vehicle_id)
    return all_paths

def return_nodes(manager, routing, solution, vehicle_id):
    """returns nodes sorted with the travel."""
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(vehicle_id)
    plan_output = 'Route for vehicle 0:\n'
    vrp_nodes = []
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += ' {} ->'.format(manager.IndexToNode(index))
        vrp_nodes.append(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(manager.IndexToNode(index))
    vrp_nodes.append(manager.IndexToNode(index))
    print(plan_output)
    plan_output += 'Route distance: {}miles\n'.format(route_distance)
    #print(tsp_nodes)
    return vrp_nodes


def print_paths_to_grid(data, nodes, vrp_nodes_path):
    color_list = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    for  vehicle_id in range(data['num_vehicles']):
        color = color_list[vehicle_id % len(color_list)]
        print_grid_to_map(nodes, vrp_nodes_path[vehicle_id], color)
    plt.show()

def print_grid_to_map(nodes, tsp_path, color):
	x_axis = []
	y_axis = []
	# convert points to coords
	for n in nodes:
		x, y = n
		x_axis.append(x)
		y_axis.append(y)
	plt.plot(x_axis, y_axis, 'ro')
	plt.show(block=False)

	for n in tsp_path:
		x, y = nodes[n]
		x_axis.append(x)
		y_axis.append(y)
		#print("Node is %s and coords are %s" %(n, nodes[n]))
	print(len(x_axis))
	print(len(y_axis))
	for n in range(0, len(tsp_path)-1):
		plt.plot([x_axis[tsp_path[n]], x_axis[tsp_path[n+1]]], [y_axis[tsp_path[n]], y_axis[tsp_path[n+1]]], color)
		plt.draw()
		plt.pause(0.2)


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    max_route_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print('Maximum of the route distances: {}m'.format(max_route_distance))


def main():
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data = create_equal_distance()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)
        vrp_nodes_path = get_vrp_nodes_path(data, manager, routing, solution)
        nodes = create_grid_points()
        print_paths_to_grid(data, nodes, vrp_nodes_path)


if __name__ == '__main__':
    main()
