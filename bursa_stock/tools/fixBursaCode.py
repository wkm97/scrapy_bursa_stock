
# Bursa Malaysia code mismatch with the one collected in bursamarketplace
from pymongo import ReturnDocument

def fixBursaCode(collection, code):
    if(collection.find_one({'bursacode': code})):
        return True
    else:
        old_code = code[1:]
        result = collection.find_one_and_update(
            {'bursacode': old_code},
            {'$set': {'bursacode': code}},
            return_document=ReturnDocument.AFTER)
        if(result is not None):
            return True
        else:
            return False