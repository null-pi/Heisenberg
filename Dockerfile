# Heisenberg System Core Dockerfile
# This Dockerfile sets up a container for the Heisenberg System Core, including OpenJDK 21, code-server, and Google Chrome.
# It installs necessary dependencies and sets up the environment for running the Heisenberg System Core.

# Base image
FROM debian:bookworm

# Set the working directory
WORKDIR /app

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Run system updates and install necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget curl gnupg ca-certificates software-properties-common \
    tigervnc-standalone-server \
    tigervnc-common \
    fluxbox \
    dbus-x11 \
    xterm \
    novnc \
    websockify \
    # Install python3-full and python3-pip for Python support
    python3 \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel \
    python3-pip && \
    # Add google-chrome repository
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    # Download code-server
    curl -fOL https://github.com/coder/code-server/releases/download/v4.91.1/code-server_4.91.1_amd64.deb && \
    # Install code-server and Google Chrome
    apt-get update && \
    apt-get install -y ./code-server_4.91.1_amd64.deb google-chrome-stable && \
    # Clean up unnecessary files
    rm ./code-server_4.91.1_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Install OpenJDK 21
RUN wget https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.3%2B9/OpenJDK21U-jre_x64_linux_hotspot_21.0.3_9.tar.gz -O /tmp/openjdk.tar.gz && \
    mkdir -p "${JAVA_HOME}" && \
    tar -xzf /tmp/openjdk.tar.gz -C "${JAVA_HOME}" --strip-components=1 && \
    rm /tmp/openjdk.tar.gz


COPY requirements.txt /app/.heisenberg-system-core/requirements.txt


RUN python3 -m venv /app/.heisenberg-system-core/venv && \
    . /app/.heisenberg-system-core/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/.heisenberg-system-core/requirements.txt && \
    playwright install-deps

# Copy the source code to the container
COPY ./src /app/.heisenberg-system-core

# Copy the start script to the working directory
COPY start.sh .
RUN chmod +x start.sh

ENTRYPOINT ["./start.sh"]
