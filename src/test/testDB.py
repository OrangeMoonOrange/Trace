import sqlite3


def update():
    output_filename="../../temp/skeleton_maps/skeleton_map_1m.db"
    conn = sqlite3.connect(output_filename)
    cur = conn.cursor()
    node_id = 0
    edge_id = 0
    segment_id = 0
    intersection_id=0
    cursor= cur.execute("SELECT max(id) from nodes")
    for x in cursor:
        node_id=x[0]

    cur.execute("SELECT max(id) from edges")
    for x in cursor:
        edge_id = x[0]

    cur.execute("SELECT max(id) from segments")
    for x in cursor:
        segment_id = x[0]

    cur.execute("SELECT max(node_id) from intersections")
    for x in cursor:
        intersection_id = x[0]

    print (node_id,edge_id,segment_id,intersection_id)





    conn.close()
if __name__ == "__main__":
    update()