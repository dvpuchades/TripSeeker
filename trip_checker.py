# takes tuples of (go_date, back_date)
# and returns the number of days that they overlap
def get_matching_days(*args):
    matching_days = args[0]
    for i in range(1, len(args)):
        days = args[i]
        if days[1] < matching_days[0] or days[0] > matching_days[1]:
            return 0
        if days[0] > matching_days[0]:
            matching_days = (days[0], matching_days[1])
        if days[1] < matching_days[1]:
            matching_days = (matching_days[0], days[1])
    return (matching_days[1] - matching_days[0]).days

def get_matching_days_in_list(trip, list_of_trips):
    matching_days = get_matching_days((trip.outbound.departureTime, trip.inbound.departureTime), (list_of_trips[0].outbound.departureTime, list_of_trips[0].inbound.departureTime))
    for other_trip in list_of_trips[1:]:
        days = get_matching_days((trip.outbound.departureTime, trip.inbound.departureTime), (other_trip.outbound.departureTime, other_trip.inbound.departureTime))
        if days < matching_days:
            matching_days = days
    return matching_days

def check_trip(trip, list_of_trips) -> bool:
    for other_trip in list_of_trips:
        matching_days = get_matching_days((trip.outbound.departureTime, trip.inbound.departureTime), (other_trip.outbound.departureTime, other_trip.inbound.departureTime))
        if matching_days == 0:
            return False
    return True

def equals(combination_a, combination_b):
    if len(combination_a) != len(combination_b):
        return False
    for trip_a in combination_a:
        if trip_a not in combination_b:
            return False
    return True

def remove_duplicates(list_of_combinations):
    new_list = []
    for combination in list_of_combinations:
        is_in_list = False
        for other_combination in new_list:
            if equals(combination, other_combination):
                is_in_list = True
                break
        if not is_in_list:
            new_list.append(combination)
    return new_list

class TripChecker:
    def __init__(self, trips):
        self.origins = {trip.outbound.origin for trip in trips}
        self.trips = trips
        self.all_possible_combinations = [[trip] for trip in trips]
        # get ready
        self._compound_combinations()
        self._remove_invalid_combinations()

    def _compound_combinations(self):
        for trip in self.trips:
            for combination in self.all_possible_combinations:
                if trip not in combination and check_trip(trip, combination) and trip.outbound.destination == combination[0].outbound.destination:
                    # combination works as a reference
                    # so it will update self.all_possible_combinations
                    combination.append(trip)
        self.all_possible_combinations = remove_duplicates(self.all_possible_combinations)

    # remove combinations that don't have all the origins
    def _remove_invalid_combinations(self):
        valid_combinations = [combination for combination in self.all_possible_combinations]
        for combination in self.all_possible_combinations:
            cities_envolved = {trip.outbound.origin for trip in combination}
            cities_envolved.add(combination[0].outbound.destination)
            for city in self.origins:
                if city not in cities_envolved:
                    valid_combinations.remove(combination)
                    break
        self.all_possible_combinations = valid_combinations

    def get_max_days_combinations(self):
        max_days_combinations = []
        for combination in self.all_possible_combinations:
            combination_origins = [trip.outbound.origin for trip in combination]
            repeated_origins = [origin for origin in combination_origins if combination_origins.count(origin) > 1]
            new_combination = []
            for trip in combination:
                if trip.outbound.origin not in repeated_origins:
                    new_combination.append(trip)
                else:
                    sharing_origin_trips = [other_trip for other_trip in combination if other_trip.outbound.origin == trip.outbound.origin]
                    combination_without_this_origin = [other_trip for other_trip in combination if other_trip.outbound.origin != trip.outbound.origin]
                    if combination_without_this_origin != []:
                        top_days_trip = sharing_origin_trips[0]
                        top_days = get_matching_days_in_list(top_days_trip, combination_without_this_origin)
                        for other_trip in sharing_origin_trips[1:]:
                            days = get_matching_days_in_list(other_trip, combination_without_this_origin)
                            if days > top_days:
                                top_days = days
                                top_days_trip = other_trip
                    else:
                        top_days_trip = sharing_origin_trips[0]
                        top_days = (top_days_trip.inbound.departureTime - top_days_trip.outbound.departureTime).days
                        for other_trip in sharing_origin_trips[1:]:
                            days = (other_trip.inbound.departureTime - other_trip.outbound.departureTime).days
                            if days > top_days:
                                top_days = days
                                top_days_trip = other_trip
                    new_combination.append(top_days_trip)
            max_days_combinations.append(list(set(new_combination)))
        return max_days_combinations

    def get_best_price_combinations(self):
        best_price_combinations = []
        for combination in self.all_possible_combinations:
            combination_origins = [trip.outbound.origin for trip in combination]
            repeated_origins = {origin for origin in combination_origins if combination_origins.count(origin) > 1}
            new_combination = []
            for trip in combination:
                if trip.outbound.origin not in repeated_origins:
                    new_combination.append(trip)
                else:
                    sharing_origin_trips = [other_trip for other_trip in combination if other_trip.outbound.origin == trip.outbound.origin]
                    combination_without_this_origin = [other_trip for other_trip in combination if other_trip.outbound.origin != trip.outbound.origin]
                    top_price_trip = sharing_origin_trips[0]
                    top_price = top_price_trip.totalPrice
                    for other_trip in sharing_origin_trips[1:]:
                        price = other_trip.totalPrice
                        if price < top_price:
                            top_price = price
                            top_price_trip = other_trip
                    new_combination.append(top_price_trip)
            best_price_combinations.append(list(set(new_combination)))
        return best_price_combinations

def get_combination_days(combination):
    combined_days = get_matching_days_in_list(combination[0], combination)
    for trip in combination[1:]:
        days = get_matching_days_in_list(trip, combination)
        if days < combined_days:
            combined_days = days
    return combined_days

def get_total_price(combination):
    total_price = 0
    for trip in combination:
        total_price += trip.totalPrice
    return total_price

def print_combinations(combinations, top=-1):
    for combination in combinations:
        if top == 0:
            break
        top -= 1
        print(combination[0].outbound.destinationFull, ". ", get_combination_days(combination), " days, ", "{:.2f}".format(get_total_price(combination)), "€")
        for trip in combination:
            print("Origin: ", trip.outbound.originFull, "Price: ", "{:.2f}".format(trip.totalPrice), "From: ", trip.outbound.departureTime.strftime("%d/%m/%Y"), "To: ", trip.inbound.departureTime.strftime("%d/%m/%Y"))

def sort_by_price(combination_list):
    return sorted(combination_list, key=lambda combination: get_total_price(combination))

def sort_by_days(combination_list):
    return sorted(combination_list, key=lambda combination: get_combination_days(combination), reverse=True)