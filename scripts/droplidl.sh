calldir=$(dirname $0)
if [ $calldir = "." ]; then
   cwd=$PWD 
   rootdir=$(dirname $cwd)
else
   cwd=$PWD/$calldir
   rootdir=$(dirname $cwd)
fi
sudo docker-compose -f $rootdirdocker-compose-lidl.yml down
