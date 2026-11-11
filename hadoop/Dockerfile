FROM debian:bookworm-slim

ARG HADOOP_VERSION=3.4.1
ARG TARGETARCH

RUN apt-get update && apt-get install -y --no-install-recommends \
      openjdk-17-jre-headless python3 openssh-server openssh-client \
      curl ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-${TARGETARCH}
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

RUN set -eux; \
    if [ "$TARGETARCH" = "arm64" ]; then SUFFIX="-aarch64"; else SUFFIX=""; fi; \
    curl -fsSL "https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}${SUFFIX}.tar.gz" \
      | tar -xz -C /opt; \
    mv /opt/hadoop-${HADOOP_VERSION} $HADOOP_HOME; \
    echo "export JAVA_HOME=${JAVA_HOME}" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

RUN useradd -m -s /bin/bash hadoop && usermod -p '*' hadoop

USER hadoop
RUN mkdir -p ~/.ssh && chmod 700 ~/.ssh \
    && ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519 \
    && cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys \
    && chmod 600 ~/.ssh/authorized_keys \
    && printf "Host *\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n" > ~/.ssh/config

USER root
RUN mkdir -p /run/sshd /data/input /data/output && chown -R hadoop:hadoop /data
RUN printf "export JAVA_HOME=%s\nexport HADOOP_HOME=%s\nexport PATH=\$PATH:%s/bin\n" \
    "$JAVA_HOME" "$HADOOP_HOME" "$HADOOP_HOME" | tee -a /home/hadoop/.bashrc >> /home/hadoop/.profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
