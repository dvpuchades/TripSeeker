from ryanair import Ryanair
from datetime import date, timedelta
import re

ryanair = Ryanair("EUR")

class TripSeeker:
    def __init__(self, min_days, max_days, init_date, finish_date, current_location, wish_list=None):
        self.min_days = min_days
        self.max_days = max_days
        self.init_date = init_date
        self.finish_date = finish_date
        self.current_location = current_location
        self.wish_list = wish_list
        self.any_destination = (wish_list is None)
        self.trips = []
        # get ready
        self._get_trips()

    # API only returns the cheapest trip for each destination
    # fetching data for each day to avoid missing interesting flights
    def _get_trips(self):
        one_day = timedelta(days=1)
        current_day = date.fromisoformat(self.init_date)
        end_day = date.fromisoformat(self.finish_date)
        while current_day < end_day:
            current_return_day = current_day + one_day
            while current_return_day <= (current_day + timedelta(days=self.max_days)):
                dates = [current_day + timedelta(days=i) for i in range(self.min_days, self.max_days + 1)]
                trips = ryanair.get_return_flights(self.current_location, current_day, current_day, current_return_day, current_return_day)
                if self.any_destination:
                    self.trips += trips
                else:
                    self.trips += [trip for trip in trips if trip.outbound.destination in self.wish_list]
                current_return_day += one_day
            current_day += one_day    

    def sort_by_price(self):
        self.trips.sort(key=lambda trip: trip.totalPrice)

    def print(self, top=10):
        index = 0
        for trip in self.trips:
            print("Destination: ", trip.outbound.destinationFull, "Price: ", "{:.2f}".format(trip.totalPrice), "From: ", trip.outbound.departureTime.strftime("%d/%m/%Y"), "To: ", trip.inbound.departureTime.strftime("%d/%m/%Y"))
            if index == top:
                break
            index += 1