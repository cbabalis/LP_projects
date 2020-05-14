""" Module which contains operations for optimization problems of
or tools.

:author: Charalampos Babalis
"""


from __future__ import print_function
# from ortools.constraint_solver import routing_enums_pb2
# from ortools.constraint_solver import pywrapcp
from scipy.spatial import distance
import matplotlib.pyplot as plt
import json
import pdb


def create_data_model(distance_matrix, num_vehicles):
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = distance_matrix
    data['num_vehicles'] = num_vehicles
    data['depot'] = 0
    return data


def read_model_from_file(a_file):
    """ Method to read the data model from a file.

    Parameters
    ----------
    a_file : str
        The filename (relative path) of the file to be read.

    Returns
    -------
    data
        a json file containing the model.
    """
    with open(a_file) as json_file:
        data = json.load(json_file)
        return data


def write_model_to_file(data, a_file):
    """ Method to write model to a file.

    Parameters
    ----------
    data : dictionary
        The data model.
    a_file : str
        The filename (relative path) of the file to be written.

    """
    with open(a_file, 'w') as outfile:
        json.dump(data, outfile)


def print_route_solution():
    """ Method to print a route solution to screen."""
    pass


def calc_matrix_euclidean_distance(points_matrix):
    """ Method to calculate the euclidean distance for a matrix.

    Parameters
    ----------
    points_matrix : list
        A matrix containing point coordinates (x,y)

    Returns
    -------
    distance_matrix : list
        A list which contains lists with the distance between the
        points given to the points_matrix (input).
    """
    distance_matrix = []
    row_matrix = []
    for point_a in points_matrix:
        for point_b in points_matrix:
            dst = distance.euclidean(point_a, point_b)
            row_matrix.append(dst)
        distance_matrix.append(row_matrix)
        row_matrix = []
    return distance_matrix


def create_simple_grid(x_dim, y_dim):
    """ Method to create a grid of points of equal distance.

    Parameters
    ---------
    x_dim : int
        x dimension of the grid.
    y_dim : int
        y dimension of the grid.

    Returns
    -------
    points_matrix : list
        a list of tuples (x,y) representing the coordinates of points.
    """
    points_matrix = []
    for i in range(0, x_dim):
        for j in range(0, y_dim):
            points_matrix.append((i, j))
    return points_matrix


def write_grid_to_file(points_matrix, output_file):
    """ Method to write a grid's points to a file.
    Parameters
    ---------
    points_matrix : list
        a list of tuples (x,y) representing the coordinates of points.
    output_file : str
        the filename where the grid points will be written.
    """
    with open(output_file, 'w') as outfile:
        for point in points_matrix:
            coords = str(point)
            outfile.write("%s\n" % coords)
        #outfile.write(','.join('%s %s' % x for x in points_matrix))


def read_grid_from_file(input_file):
    """ Method to read points from a file and build a grid with them.
    
    Parameters
    ----------
    input_file : str
        The filepath with the grid points.
    
    Returns
    -------
    points_matrix : list
        a list of tuples (x,y) representing the coordinates of points.
    """
    points_matrix = []
    with open(input_file, 'r') as infile:
        content = infile.read().splitlines()
        for coord in content:
            points_matrix.append(eval(coord))
    return points_matrix


def get_all_routes(data, manager, routing, solution):
    """ Method to get the routes of all nodes.

    Parameters
    ----------
    data : dictionary
        The model containing the data for the optimization model.
    manager : ortools objects
    routing : ortools routing
    solution : ortools solution as found.

    Returns
    -------
    all_paths : dictionary
        A dictionary full of key:path pairs.
    """
    all_paths = {}
    for vehicle_id in range(data['num_vehicles']):
        all_paths[vehicle_id] = get_single_route_nodes(
                                    manager, routing, solution, vehicle_id)
    return all_paths


def get_single_route_nodes(manager, routing, solution, vehicle_id):
    """ Method to get the nodes of a single route.

    Parameters
    ----------
    manager : ortools objects
    routing : ortools routing
    solution : ortools object representing the found solution.
    vehicle_id : int, the id of the vehicle

    Returns
    -------
    solution_nodes: list
        A list of all nodes that consist the solution.
    """
    print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(vehicle_id)
    solution_nodes = []
    route_distance = 0
    while not routing.IsEnd(index):
        solution_nodes.append(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    solution_nodes.append(manager.IndexToNode(index))
    return solution_nodes


def print_grid(nodes, color='ro'):
    """ Method to print a simple grid.

    Parameters
    ----------
    nodes : list
        A list of (x, y) tuples representing nodes' coordinates

    Returns
    -------
    x_axis : list
    y_axis : list
    """
    x_axis = []
    y_axis = []
    # convert points to coords
    for n in nodes:
        x, y = n
        x_axis.append(x)
        y_axis.append(y)
    plt.plot(x_axis, y_axis, color)
    plt.show(block=False)
    return (x_axis, y_axis)


def print_solution_to_grid(nodes, solution_path, axis, color):
    """ Method to print the solution to grid."""
    x_axis, y_axis = axis
    for n in solution_path:
        x, y = nodes[n]
        x_axis.append(x)
        y_axis.append(y)
        # print("Node is %s and coords are %s" %(n, nodes[n]))
    for n in range(0, len(solution_path)-1):
        plt.plot([x_axis[solution_path[n]],
                  x_axis[solution_path[n+1]]],
                  [y_axis[solution_path[n]],
                  y_axis[solution_path[n+1]]],
                  color)
        plt.draw()
        plt.pause(0.1)


def print_paths_to_grid(data, nodes, solutions_path):
    """ Method to print the paths to an already printed grid."""
    for vehicle_id in range(data['num_vehicles']):
        color = get_plot_color(vehicle_id)
        axis = print_grid(nodes, color)
        print_solution_to_grid(nodes, solutions_path, axis, color)
    plt.show()


def get_plot_color(vehicle_id):
    """ Method which returns a plot color."""
    color_list = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    return color_list[vehicle_id % len(color_list)]
