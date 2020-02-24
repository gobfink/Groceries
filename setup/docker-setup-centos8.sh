#! /bin/bash
docker_repo_url=https://download.docker.com/linux/centos/docker-ce.repo
containerd_rpm_url=https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.2.6-3.3.el7.x86_64.rpm

echo "Setting up docker repo - $docker_repo_url"
sudo dnf config-manager --add-repo=$docker_repo_url

echo "Installing containerd - $containerd_rpm_url"
sudo dnf install $containerd_rpm_url

echo "Installing docker-ce"
sudo dnf install docker-ce

echo "enabling docker service"
sudo systemctl enable --now docker

echo "Setting up docker group"
sudo usermod -aG docker $USER
newgrp docker << AS_DOCKER

	docker run hello-world

AS_DOCKER
