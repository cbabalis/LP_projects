#!/usr/bin/env python

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
import pdb


def read_city_names(city_names_file):
    """ method to read a file full of city names and returns them as
    geolocator objects.
    """
    locations = []
    return locations


def modify_data_for_google_or(city_names):
    """ Method which computes the distance of each city with the others
    and creates a dictionary according to the specs of or_tools.
    :param city_names: list of city names
    """
    # create a list for the geolocator objects and a matrix containing
    # all distances between the cities
    cities = []
    distance_matrix = []
    geolocator = Nominatim(user_agent="babis", timeout=10)

    # create a list of cities instead of city names
    for name in city_names:
        #time.sleep(1)
        city = geolocator.geocode(name)
        cities.append(city)

    # create the distances between cities and have a complex dictionary
    create_distance_matrix(cities, distance_matrix)
    # read for use with or_tools
    # TODO here

    # return the dictionary
    return distance_matrix


def create_distance_matrix(cities, distance_matrix):
    """ fills the distance matrix with the distances between the cities.
    """
    one_city_distances = []
    for city in cities:
        for another_city in cities:
            dist = compute_distance(city, another_city)
            one_city_distances.append(dist)
        distance_matrix.append(one_city_distances)
        one_city_distances = []


def compute_distance(city_a, city_b):
    city_a_loc = (city_a.latitude, city_a.longitude)
    city_b_loc = (city_b.latitude, city_b.longitude)
    distance = geodesic(city_a_loc, city_b_loc)
    return distance.km


def main():
    city_names = ["Athens", "Thebes", "Lamia", "Volos", "Kozani", "Giannena", "Agrinio", "Korinthos"]
    distance_matrix = modify_data_for_google_or(city_names)
    print(distance_matrix)


if __name__ == '__main__':
    main()
