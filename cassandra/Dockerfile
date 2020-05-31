FROM centos:latest
MAINTAINER alexkayser87@yahoo.com

# Add Apache Cassandra to the repo list
COPY cassandra.repo /etc/yum.repos.d

# Install dependencies
RUN dnf -y install \
	java-1.8.0-openjdk-devel \
	python2 \
	cassandra

# Rename our cluster
RUN sed -i 's/Test Cluster/GroceriesCluster/g' /etc/cassandra/default.conf/cassandra.yaml

# Specify the number of tokens
RUN sed -i 's/num_tokens: 256/num_tokens: 24/g' /etc/cassandra/default.conf/cassandra.yaml

# Enable security
RUN sed -i 's/AllowAllAuthenticator/PasswordAuthenticator/g' /etc/cassandra/default.conf/cassandra.yaml
RUN sed -i 's/AllowAllAuthorizer/CassandraAuthorizer/g' /etc/cassandra/default.conf/cassandra.yaml

# Teaches Cassandra about network topology and allows for replicas around cluster
RUN sed -i 's/SimpleSnitch/GossipingPropertyFileSnitch/g' /etc/cassandra/default.conf/cassandra.yaml
