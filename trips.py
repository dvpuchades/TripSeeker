from trip_seeker import TripSeeker

if __name__ == '__main__':
    seeker = TripSeeker(14, 50, '2023-03-04', '2023-04-02', 'VLC', ['ORK', 'DUB'])
    seeker.sort_by_price()
    seeker.print()