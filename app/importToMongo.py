import os 

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import libraries
from pymongo import MongoClient
import pandas as pd

# Import custom modules
from uploadToS3 import *

def connectToDB():
    mongouri = os.getenv('MONGODB_URI')

    try: 
        client = MongoClient(mongouri)
        client.server_info()
        status = 'Connected to the database'
    
    except Exception as e:
        status = 'Error connecting to the database: ' + str(e)

    return (status, client)

def importToMongo(file, flags):
    print('flags', flags)
    (status, client) = connectToDB()
    database = os.getenv('MONGODB_DATABASE')

    if status != 'Connected to the database':
        return status
    
    db = client.get_database(database)
    # define the collections we will be using
    postCollection = db['posts']

    # read the excel file and convert each row into
    data = pd.read_excel(file)

    # the columns in the excel file are not the same as the columns in the post collection
    # so we need to rename the columns
    data.rename(columns={'subject': 'title', 'body': 'content'}, inplace=True)

    # EXAMPLE UPDATE OF POST COLLECTION
    # data for the post collection
    postData = data[['postId','title','content']]

    # lookup the post in the post collection by SKU. If it exists, update it. If it doesn't exist, create it.
    data['postId'] = None
    for index, row in postData.iterrows():
        if row['title'] == '' or row['content'] == '':
            continue
        postId = row['postId']
        postDocument = postCollection.find_one({'_id': postId})
        if postDocument is None:
            postDocument = postCollection.insert_one(row.to_dict())
            # update data with the post id
            data.at[index, 'postId'] = postDocument.inserted_id
        else:
            postCollection.update_one({'_id': postId}, {'$set': row.to_dict()})
            # update data with the post id
            data.at[index, 'postId'] = postDocument['_id']

    # IMAGES
    # delete all images from S3 if flags['delete-images'] is true
    if 'delete-images' in flags:
        print('deleting images')
        for index, row in data.iterrows():
            if row['postId'] == '':
                continue
            postId = row['postId']
            postDocument = postCollection.find_one({'_id': postId, 'images': {'$exists': True}})
            if postDocument is None:
                continue
            for image in postDocument['images']:
                deleteFromS3(image['imageFile'])
            postCollection.update_one({'_id': postId}, {'$set': {'images': []}})

    # skip image upload if flags['skip-image-import'] is true
    if 'skip-image-import' not in flags:
        print('uploading images')
        
        # for each row in the data, upload the image to S3 and update the post document's image array with 
        # an object containing the url of the image in imageFile and the variant in the imageCaption
        for index, row in data.iterrows():
            # if any of the required fields are blank, skip the image upload
            if row['image'] == '' or row['postId'] == '':
                continue
            postId = row['postId']
            imageFile = row['image']
            # verify that the image isn't already in the images array
            # create filename
            oldFilename = imageFile.split('/')[-1].split('?')[0]
            if env == 'dev':
                filename = 'dev-post/' + str(postId) + '/' + oldFilename + '.png'
            else:
                filename = 'post/' + str(postId) + '/' + oldFilename + '.png'
            postDocument = postCollection.find_one({'_id': postId, 'images': {'$elemMatch': {'imageFile': filename}}})

            if postDocument is None:
                uploadedImageFile = uploadToS3(imageFile, filename, flags)
                postCollection.update_one({'_id': row['postId']}, {'$push': {'images': {'imageFile': uploadedImageFile, 'imageCaption': ''}}})
            else:
                continue

    return data.to_html() 