#! /bin/bash
docker_repo_url=https://download.docker.com/linux/centos/docker-ce.repo
containerd_rpm_url=https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.2.6-3.3.el7.x86_64.rpm
docker_compose_url=https://github.com/docker/compose/releases/download/1.25.0/docker-compose-`uname -s`-`uname -m`
docker_compose_destination=/usr/local/bin/docker-compose

echo "Setting up docker repo - $docker_repo_url"
sudo dnf config-manager --add-repo=$docker_repo_url

echo "Installing containerd - $containerd_rpm_url"
sudo dnf install $containerd_rpm_url

echo "Installing docker-ce"
sudo dnf install docker-ce

echo "enabling docker service"
sudo systemctl enable --now docker

echo "Setting up docker-compose"
sudo dnf install curl
sudo curl -L $docker_compose_url -o $docker_compose_destination
sudo chmod u+x $docker_compose_destination
sudo chown $USER:$USER $docker_compose_destination

docker-compose --version

echo "Setting up docker group"
sudo usermod -aG docker $USER
newgrp docker << AS_DOCKER
	docker run hello-world
AS_DOCKER
