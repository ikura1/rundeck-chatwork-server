NAME=rundeck
FUNCTION=rundeck
ENVFILE=.env

deploy:
	gcloud beta functions deploy ${NAME} --env-vars-file=.env --entry-point=${FUNCTION} --trigger-http
