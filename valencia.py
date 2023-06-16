from datetime import datetime, timedelta
import argparse

from ryanair import Ryanair
from tabulate import tabulate

api = Ryanair()

def get_next_saturday() -> datetime:
    today = datetime.today().date().weekday()
    if today == 5:
        return today
    elif today < 5:
        return datetime.today() + timedelta(days=(5 - today))
    else:
        return datetime.today() + timedelta(days=(today + 7))

def get_two_weeks_trip(day: datetime):
    two_weeks_after = day + timedelta(days=14)

    trips = api.get_cheapest_return_flights("ORK", day, day, two_weeks_after, two_weeks_after)

    for trip in trips:
        if trip.outbound.destination == 'VLC':
            # print("Destination: ", trip.outbound.destinationFull, "Price: ", "{:.2f}".format(trip.totalPrice), "From: ", trip.outbound.departureTime.strftime("%d/%m/%Y"), "To: ", trip.inbound.departureTime.strftime("%d/%m/%Y"))
            trip_info = {
                "arrival": trip.outbound.departureTime,
                "departure": trip.inbound.departureTime,
                "price": trip.totalPrice
            }
            return trip_info
        
def print_next_trips(weeks, sort_by_cheaper=False):
    next_saturday = get_next_saturday()
    trips = []
    for week in range(weeks + 1):
        trips.append(get_two_weeks_trip(day=(next_saturday + timedelta(weeks=week))))
    if sort_by_cheaper:
        trips = sorted(trips, key=lambda t: t['price']) 
    print(tabulate(trips, headers="keys"))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seeks next flights to Valencia from Cork.')
    parser.add_argument('--weeks', type=int, default=8, help='Number of weeks forward to seek a trip.')
    parser.add_argument('--cheapest', dest='cheapest', action=argparse.BooleanOptionalAction, help='Sorts by cheaper flights')
    args = parser.parse_args()
    print_next_trips(args.weeks, sort_by_cheaper=args.cheapest)