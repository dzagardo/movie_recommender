set -e
echo "Starting the deployment.."

pwd

instance_a="recommender-a"
instance_b="recommender-b"

echo "Trying to pull the latest repo..."

if [[ -d "./group-project-f22-thelandofharrypottersamazingendgamept2" ]]
then
    cd group-project-f22-thelandofharrypottersamazingendgamept2
    git stash
    git checkout origin/main
    git reset --hard origin/main
    git pull origin main
else
    ssh-keyscan github.com >> ~/.ssh/known_hosts
    git clone git@github.com:cmu-seai/group-project-f22-thelandofharrypottersamazingendgamept2.git
    cd group-project-f22-thelandofharrypottersamazingendgamept2
fi
echo "Pulled the latest repo!"

echo "=========Install essential requirements========="
pip install -r requirements.txt
echo "Running pipeline..."
echo "=========Pipe 1/3 running========="
python3 model_training_and_evaluation_codes/model_training_pipe0.py
echo "=========Pipe 2/3 running========="
python3 model_training_and_evaluation_codes/data_processing_pipe1.py model_training_and_evaluation_codes/data/kafka_ratings.txt model_training_and_evaluation_codes/data/
echo "=========Pipe 3/3 running========="
python3 model_training_and_evaluation_codes/model_training_pipe2.py model_training_and_evaluation_codes/data/
echo "=========Pipeline Running Done========="



echo "====Bringing recommender service - instance a  DOWN....."
docker-compose stop $instance_a
docker-compose rm -f $instance_a
echo "===Bringing recommender service - instance a  UP....."
docker-compose build $instance_a
docker-compose up -d $instance_a

echo "==Bringing recommender service - instance b  DOWN....."
docker-compose stop $instance_b
docker-compose rm -f $instance_b
echo "=Bringing recommender service - instance b  UP....."
docker-compose build $instance_b
docker-compose up -d $instance_b


# if [ -z `docker-compose ps -q $instance_a` ] || [ -z `docker ps -q --no-trunc | grep $(docker-compose ps -q $instance_a)` ]; then
#   echo "Instance A down still, failed"
#   exit 1
# else
#   echo "Instance A UP, check passed"
# fi

# if [ -z `docker-compose ps -q $instance_b` ] || [ -z `docker ps -q --no-trunc | grep $(docker-compose ps -q $instance_b)` ]; then
#   echo "Instance B down still, failed"
#   exit 1
# else
#   echo "Instance B UP, check passed"
# fi

echo "Both instances up now! Exiting.."