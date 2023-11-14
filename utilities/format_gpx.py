from .haversine import haversine


def format_gpx(gpx):
    distance_elevation_list = [{'Distance': 0.0, 'Elevation': 0.0}]

    distance = 0
    elevation = 0

    for track in gpx.tracks:
        for segment in track.segments:
            points = segment.points
            for i in range(0, len(points)):
                item1 = points[i]
                if i + 1 < len(points):
                    item2 = points[i + 1]
                    # Do something with item1 and item2
                    hav = haversine(item1.longitude, item1.latitude,
                                    item2.longitude, item2.latitude)
                    distance += hav

                    elevation_difference = item2.elevation - item1.elevation

                    if elevation_difference > 0:
                        elevation += elevation_difference

                    distance_elevation_list.append(
                        {'Distance': distance, 'Elevation': elevation})

    return distance_elevation_list
