from google.cloud import datastore

# Have to also create a master entity


def Refresh(datastore_client):
    global client
    client = datastore_client
    ClearUsers()
    ClearCourses()


def ClearUsers():
    query = client.query(kind='user')
    print('made it past query')
    print('made it past query key filter')
    results = list(query.fetch())
    for result in results:
        key = result.key
        client.delete(key)


def ClearCourses():
    query = client.query(kind='course')
    print('made it past query for all courses in clearcourses')
    print('made it past query key filter')
    results = list(query.fetch())
    for result in results:
        key = result.key
        client.delete(key)
