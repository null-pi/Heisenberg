#!/bin/bash
set -e

echo "--- Starting Heisenberg ---"

# Start the Heisenberg System Core application based on the environment variable
cd /app/.heisenberg-system-core && . /app/.heisenberg-system-core/venv/bin/activate
PRODUCTION=${PRODUCTION:-false}
if [ "$PRODUCTION" = "true" ]; then
    echo "Running in production mode..."
    fastapi run src/main.py --host ${SERVER_HOST:-0.0.0.0} --port ${SERVER_PORT:-8000} --workers ${WORKERS:-4}

else
    echo "Running in development mode..."
    fastapi dev src/main.py --host ${SERVER_HOST:-0.0.0.0} --port ${SERVER_PORT:-8000} --reload
fi

echo "--- VNC & CODE-SERVER STARTUP SCRIPT ---"

# --- Define Defaults from Environment or use Fallbacks ---
VNC_RES=${VNC_RESOLUTION:-1920x1080}
VNC_DEPTH=${VNC_COL_DEPTH:-24}
VNC_PORT_NUM=${VNC_PORT:-5901}
NOVNC_PORT_NUM=${NOVNC_PORT:-6901}
CODE_SERVER_PORT=${CODE_SERVER_PORT:-8443}

# --- Set up machine-id and Start D-Bus ---
# D-Bus requires a unique machine-id to run correctly.
echo "Initializing machine ID for D-Bus..."
mkdir -p /var/lib/dbus
dbus-uuidgen > /var/lib/dbus/machine-id
cp /var/lib/dbus/machine-id /etc/machine-id

# Start a user-specific D-Bus session bus, which is more reliable in containers.
echo "Starting D-Bus session bus..."
eval $(dbus-launch --sh-syntax)
sleep 1 # Give D-Bus a moment to start

# --- Configure and Start VNC Server ---
mkdir -p /root/.vnc
# Update the xstartup file to automatically launch and maximize Chrome
cat <<EOF > /root/.vnc/xstartup
#!/bin/sh
# Export the correct D-Bus session address for graphical applications
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS}"
unset SESSION_MANAGER

# Start Fluxbox in the background
fluxbox &

# Launch Google Chrome and tell Fluxbox to maximize it.
# The --start-maximized flag is a hint for the window manager.
DISPLAY=:1 google-chrome --no-sandbox --no-first-run --start-maximized

EOF
chmod +x /root/.vnc/xstartup

echo "Starting VNC server on :1 (Port: ${VNC_PORT_NUM})"
vncserver :1 -geometry ${VNC_RES} -depth ${VNC_DEPTH} -rfbport ${VNC_PORT_NUM} -localhost no -SecurityTypes None --I-KNOW-THIS-IS-INSECURE

# --- Start noVNC Web Proxy ---
echo "Starting noVNC proxy on port ${NOVNC_PORT_NUM}"
echo ">>> VNC URL: http://localhost:${NOVNC_PORT_NUM}/vnc.html?autoconnect=true"
websockify --web /usr/share/novnc/ ${NOVNC_PORT_NUM} localhost:${VNC_PORT_NUM} &

# The separate Chrome launch is now handled by xstartup, so it is removed from here.

# --- Start code-server in the Foreground ---
# This will be the main process that keeps the container alive.
echo "Starting code-server on port ${CODE_SERVER_PORT}"
echo ">>> Code Editor URL: http://localhost:${CODE_SERVER_PORT}"
code-server --bind-addr 0.0.0.0:${CODE_SERVER_PORT} --auth none

sleep 2
tail -f /root/.vnc/*.log &

# Keep the script running to prevent the container from exiting
wait
# End of script
