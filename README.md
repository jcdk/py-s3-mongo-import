# Scaffolding in Python/Flask for creating a MongoDB import and AWS S3 bucket upload app

Can be run on local with variables defined in .env or deployed to Railway and use configured environment variables.

The sample shows how to upload an excel file to a 'posts' collection. 

The excel file has columns:
| postId | subject | body            | image                              |
|--------|---------|-----------------|------------------------------------|
| 1      | Hello   | This is a story | https://en.wikipedia.org/image.jpg |

Which maps to the following schema for `posts` collection in MongoDB:
| _id | title | content         | image                                |
|-----|-------|-----------------|--------------------------------------|
| 1   | Hello | This is a story | post/`postId`/`originalfilename`.png |

## Project structure:

```
.
├── compose.yaml
├── app
    ├── static/ - css files
    ├── templates/ - html templates
    ├── app.py - flask routing
    ├── Dockerfile - Docker config
    ├── env.template - environment variables, to store S3 and MongoDB secrets
    ├── importToMongo.py - script for importing into MongoDB
    ├── requirements.txt - library requirements
    └── uploadToS3.py - script for importing file submitted to AWS S3

```

## Deploy with docker compose

```
$ docker compose up --build
```

## Stop and remove the containers

```
$ docker compose down
```

## Dev Environment Variables

Create .env file from env.template
