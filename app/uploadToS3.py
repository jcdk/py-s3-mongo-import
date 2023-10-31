import os 

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

#import libraries
import requests
from PIL import Image
import boto3
from io import BytesIO
import cfscrape

scraper = cfscrape.create_scraper()

env = os.getenv('ENV')
awsKey = os.getenv('AWS_ACCESS_KEY')
awsSecret = os.getenv('AWS_SECRET_KEY')
awsBucket = os.getenv('AWS_BUCKET')
awsRegion = os.getenv('AWS_REGION')

def uploadToS3(url, newFilename, flags = {}):

    # get the image from the url
    response = scraper.get(url)
    if response.status_code != 200:
        print('Error downloading image: ' + str(response.status_code))
        return None
    else:
        img = Image.open(BytesIO(response.content))

    # resize the image to fit a 1000x1000 canvas with a white background and center it
    width, height = img.size
    if width > height:
        new_width = 925
        new_height = int(height * (new_width / width))
    else:
        new_height = 925
        new_width = int(width * (new_height / height))

    # add padding to the image of 25px 
    img = img.resize((new_width, new_height), Image.LANCZOS)
    newImage = Image.new('RGBA', (1000, 1000), (255, 255, 255, 255))
    offset = ((1000 - new_width) // 2, (1000 - new_height) // 2)

    newImage.paste(img, offset)
    # encode newImage for s3
    buffer = BytesIO()
    newImage.save(buffer, format='PNG')
    buffer.seek(0)
    newImage = buffer

    # upload the image to S3
    s3 = boto3.client('s3', aws_access_key_id=awsKey, aws_secret_access_key=awsSecret)
    s3.put_object(Bucket=awsBucket, Key=newFilename, Body=newImage, ContentType='image/png')

    # return the url of the image
    return newFilename

def deleteFromS3(filename):
    s3 = boto3.client('s3', aws_access_key_id=awsKey, aws_secret_access_key=awsSecret)
    s3.delete_object(Bucket=awsBucket, Key=filename)