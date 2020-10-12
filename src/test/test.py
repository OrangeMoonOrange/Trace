from src.preprocessing.genTrip import Trip_get

if __name__ == '__main__':
    print Trip_get("2019-00-00", "2019-08-00").load_trip_from_db()