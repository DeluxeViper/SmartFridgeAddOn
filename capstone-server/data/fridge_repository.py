from .client import db_client
# FRIDGE REPOSITORY: Manages objects in Firestore

# REQUIRES: Course object
# EFFECTS: Converts Keys to Unicode
def convertFridge(fridge): 
    return {
    u'name': fridge['name'],
    u'items': fridge['items'],
    u'tracking': fridge['tracking'],
    u'image': fridge['image'],
    u'last_updated': fridge['last_updated']
    }    

# REQUIRES: Users Id, and Fridge Id
# EFFECTS: Retrieves the fridge subdocument under that users fridge collection 
def getDocument(user_id, fridge_id):
    return db_client.collection("users").document(user_id).collection("fridges").document(fridge_id)

# CREATE
def addFridge(user_id, fridge_id, fridge):
    doc_ref = getDocument(user_id, fridge_id)
    doc_ref.set(convertFridge(fridge))
    return doc_ref

# READ
def readFridge(user_id, fridge_id):
    doc_ref = getDocument(user_id, fridge_id)
    return doc_ref.get().to_dict()

# UPDATE
def updateFridge(user_id, fridge_id, fridge):
    doc_ref = getDocument(user_id, fridge_id)
    doc_ref.update(convertFridge(fridge))

# DELETE
def deleteFridge(user_id, fridge_id):
    doc_ref = getDocument(user_id, fridge_id)
    doc = doc_ref.get()
    doc_ref.delete()
    return doc.to_dict()