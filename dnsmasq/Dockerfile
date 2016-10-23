FROM centos:centos7

RUN yum install -y dnsmasq net-tools bind-utils wget
RUN yum install -y epel-release python-setuptools docker
RUN yum install -y python-pip
RUN pip install docker-py
ADD cns.py /cns.py
ADD entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
