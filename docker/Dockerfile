FROM centos:7

RUN yum -y update
RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm
RUN yum install -y python36u python36u-libs python36u-devel python36u-pip
# RUN rm -f /usr/bin/python
# RUN ln -s /usr/bin/python3.6 /usr/bin/python # これだと以降のyumが使えなくなる
RUN ln -s /usr/bin/python3.6 /usr/bin/python3
RUN ln -s /usr/bin/pip3.6 /usr/bin/pip
RUN pip install --upgrade pip
RUN yum install -y unzip
RUN yum install -y gcc
RUN yum install -y vim
RUN yum install -y nkf
# RUN yum install -y nginx


# Google Chrome
RUN touch /etc/yum.repos.d/google-chrome.repo
RUN ( \
        echo "[google-chrome]"; \
        echo "name=google-chrome"; \
        echo "baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64"; \
        echo "enabled=1"; \
        echo "gpgcheck=1"; \
        echo "gpgkey=https://dl.google.com/linux/linux_signing_key.pub"; \
    ) > /etc/yum.repos.d/google-chrome.repo
RUN yum install -y google-chrome-stable
RUN yum install -y libOSMesa google-noto-cjk-fonts

RUN cd /tmp && \
    wget https://chromedriver.storage.googleapis.com/2.46/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/
RUN yum install -y libX11 GConf2 fontconfig

# selenium && scrape
RUN pip install selenium
RUN pip install pyvirtualdisplay
RUN pip install beautifulsoup4
RUN pip install lxml
RUN pip install python-dotenv
RUN pip install requests

# django
RUN pip install django==2.1
RUN pip install uwsgi


CMD ["/bin/bash"]
