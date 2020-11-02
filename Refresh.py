from google.cloud import datastore

def Refresh(datastore_client):
    global client
    client = datastore_client
    ClearUsers()

def ClearUsers():
    query = client.query(kind='user')
    print('made it past query')
    # query.key_filter((client.key('course', course)), '=')
    print('made it past query key filter')
    results = list(query.fetch())
    for result in results:
        key = result.key
        print(key)