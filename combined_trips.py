from trip_seeker import TripSeeker
from trip_checker import TripChecker, print_combinations, sort_by_price, sort_by_days

if __name__ == '__main__':
    trips = []
    origins = ['ORK', 'VLC']
    for origin in origins:
        trips += TripSeeker(2, 5, '2023-02-16', '2023-04-15', origin).trips
    trip_checker = TripChecker(trips)
    print("\n", "Best price combinations:")
    print_combinations(sort_by_price(trip_checker.get_best_price_combinations()))
    print("\n", "Max days combinations:")
    print_combinations(sort_by_days(trip_checker.get_max_days_combinations()))
