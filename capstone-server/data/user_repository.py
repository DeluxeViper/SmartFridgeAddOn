from .client import db_client
# User REPOSITORY: Manages user objects in Firestore

# REQUIRES: Course object
# EFFECTS: Converts Keys to Unicode
def convertUser(user): 
    return {
    u'authProvider': user['name'],
    u'email': user['items'],
    u'name': user['tracking'],
    u'uid': user['image'],
    }    

# REQUIRES: Users Id, and Fridge Id
# EFFECTS: Retrieves the fridge subdocument under that users fridge collection 
def getDocument(user_id):
    return db_client.collection("users").document(user_id)

# READ
def readUser(user_id):
    doc_ref = getDocument(user_id)
    return doc_ref.get().to_dict()
