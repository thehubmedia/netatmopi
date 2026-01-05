#!/bin/bash
#
# Deployment script for Netatmo Weather Plugin
# Usage: ./deploy.sh [options] <pi_hostname_or_ip>
#
# Options:
#   --password-auth    Force password authentication (skip SSH keys)
#
# This script copies the plugin to your Raspberry Pi and installs dependencies
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse options
USE_PASSWORD_AUTH=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --password-auth)
            USE_PASSWORD_AUTH=true
            shift
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}"
            echo "Usage: $0 [--password-auth] <pi_hostname_or_ip>"
            exit 1
            ;;
        *)
            PI_HOST=$1
            shift
            ;;
    esac
done

# Check that we have a hostname
if [ -z "$PI_HOST" ]; then
    echo -e "${RED}Error: Please provide Raspberry Pi hostname or IP address${NC}"
    echo "Usage: $0 [--password-auth] <pi_hostname_or_ip>"
    echo ""
    echo "Options:"
    echo "  --password-auth    Force password authentication (skip SSH keys)"
    echo ""
    echo "Examples:"
    echo "  $0 raspberrypi.local"
    echo "  $0 192.168.1.100"
    echo "  $0 --password-auth raspberrypi.local"
    exit 1
fi

PI_USER=${PI_USER:-pi}  # Default to 'pi' user, can override with env var
INKYPI_PLUGINS_DIR=${INKYPI_PLUGINS_DIR:-/home/$PI_USER/InkyPi/src/plugins}
PLUGIN_NAME="netatmo_weather"

# Set SSH options based on authentication method
if [ "$USE_PASSWORD_AUTH" = true ]; then
    SSH_OPTS="-o PreferredAuthentications=password -o PubkeyAuthentication=no"
    echo -e "${YELLOW}Using password authentication (SSH keys disabled)${NC}"
else
    SSH_OPTS=""
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Netatmo Weather Plugin Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Target: $PI_USER@$PI_HOST"
echo "Plugin directory: $INKYPI_PLUGINS_DIR"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "You'll need to configure API credentials on the Pi manually"
    echo "Or create .env file before deploying"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Test SSH connection
echo -e "${YELLOW}Testing SSH connection...${NC}"
if ! ssh $SSH_OPTS -o ConnectTimeout=5 "$PI_USER@$PI_HOST" exit 2>/dev/null; then
    echo -e "${RED}Error: Cannot connect to $PI_USER@$PI_HOST${NC}"
    echo "Please check:"
    echo "  1. Raspberry Pi is powered on and connected to network"
    echo "  2. SSH is enabled on the Pi"
    echo "  3. Hostname/IP address is correct"
    echo "  4. You can SSH manually: ssh $PI_USER@$PI_HOST"
    exit 1
fi
echo -e "${GREEN}✓ SSH connection successful${NC}"

# Create plugin directory on Pi
echo -e "${YELLOW}Creating plugin directory...${NC}"
ssh $SSH_OPTS "$PI_USER@$PI_HOST" "mkdir -p $INKYPI_PLUGINS_DIR/$PLUGIN_NAME/{templates,static}"
echo -e "${GREEN}✓ Directory created${NC}"

# Copy plugin files
echo -e "${YELLOW}Copying plugin files...${NC}"
rsync -avz --exclude='preview_*.html' --exclude='preview_*.png' -e "ssh $SSH_OPTS" inkypi-netatmo-plugin/ "$PI_USER@$PI_HOST:$INKYPI_PLUGINS_DIR/$PLUGIN_NAME/"
echo -e "${GREEN}✓ Files copied${NC}"

# Copy/merge .env file to InkyPi root if it exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Updating .env file at InkyPi root...${NC}"
    INKYPI_ROOT=$(dirname $(dirname "$INKYPI_PLUGINS_DIR"))

    # Copy our .env to a temp location
    scp $SSH_OPTS .env "$PI_USER@$PI_HOST:/tmp/netatmo_plugin.env"

    # Smart merge: only add/update keys that are missing or different
    ssh $SSH_OPTS "$PI_USER@$PI_HOST" bash << 'ENDSSH'
        INKYPI_ROOT="$(dirname $(dirname "$INKYPI_PLUGINS_DIR"))"
        TARGET_ENV="$INKYPI_ROOT/.env"
        SOURCE_ENV="/tmp/netatmo_plugin.env"

        # Create target .env if it doesn't exist
        touch "$TARGET_ENV"

        # Backup existing .env
        if [ -s "$TARGET_ENV" ]; then
            cp "$TARGET_ENV" "$TARGET_ENV.backup"
            echo "Backed up existing .env to .env.backup"
        fi

        # Track if we made any changes
        CHANGES_MADE=false
        ADDED_KEYS=()
        UPDATED_KEYS=()

        # Read each line from source .env
        while IFS= read -r line || [ -n "$line" ]; do
            # Skip empty lines and comments
            if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
                continue
            fi

            # Extract key=value
            if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
                key="${BASH_REMATCH[1]}"
                value="${BASH_REMATCH[2]}"

                # Check if key exists in target
                if grep -q "^${key}=" "$TARGET_ENV"; then
                    # Get current value
                    current_value=$(grep "^${key}=" "$TARGET_ENV" | head -1 | cut -d= -f2-)

                    # Update if different
                    if [ "$current_value" != "$value" ]; then
                        # Use sed to replace the first occurrence
                        sed -i "0,/^${key}=.*/{s|^${key}=.*|${key}=${value}|}" "$TARGET_ENV"
                        UPDATED_KEYS+=("$key")
                        CHANGES_MADE=true
                    fi
                else
                    # Key doesn't exist, add it
                    # Add section header if this is the first Netatmo key
                    if [ ${#ADDED_KEYS[@]} -eq 0 ]; then
                        echo "" >> "$TARGET_ENV"
                        echo "# Netatmo Weather Plugin credentials" >> "$TARGET_ENV"
                    fi
                    echo "${key}=${value}" >> "$TARGET_ENV"
                    ADDED_KEYS+=("$key")
                    CHANGES_MADE=true
                fi
            fi
        done < "$SOURCE_ENV"

        # Clean up
        rm -f "$SOURCE_ENV"

        # Report changes
        if [ "$CHANGES_MADE" = true ]; then
            if [ ${#ADDED_KEYS[@]} -gt 0 ]; then
                echo "Added keys: ${ADDED_KEYS[*]}"
            fi
            if [ ${#UPDATED_KEYS[@]} -gt 0 ]; then
                echo "Updated keys: ${UPDATED_KEYS[*]}"
            fi
        else
            echo "No changes needed - all keys up to date"
        fi
ENDSSH

    echo -e "${GREEN}✓ .env file updated at InkyPi root${NC}"
fi

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
# Try normal pip install first, fall back to --break-system-packages if needed
if ! ssh $SSH_OPTS "$PI_USER@$PI_HOST" "cd $INKYPI_PLUGINS_DIR/$PLUGIN_NAME && pip3 install -r requirements.txt 2>/dev/null"; then
    echo -e "${YELLOW}Using --break-system-packages (safe for dedicated Pi)...${NC}"
    ssh $SSH_OPTS "$PI_USER@$PI_HOST" "cd $INKYPI_PLUGINS_DIR/$PLUGIN_NAME && pip3 install --break-system-packages -r requirements.txt"
fi
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if config exists, if not copy example
echo -e "${YELLOW}Checking configuration...${NC}"
ssh $SSH_OPTS "$PI_USER@$PI_HOST" << 'ENDSSH'
    PLUGIN_DIR="$INKYPI_PLUGINS_DIR/$PLUGIN_NAME"
    if [ ! -f "$PLUGIN_DIR/config.yaml" ] && [ -f "$PLUGIN_DIR/config.example.yaml" ]; then
        echo "Creating config.yaml from example..."
        cp "$PLUGIN_DIR/config.example.yaml" "$PLUGIN_DIR/config.yaml"
        echo "⚠️  Please edit config.yaml with your credentials"
    fi
ENDSSH
echo -e "${GREEN}✓ Configuration checked${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. SSH to your Pi: ssh $PI_USER@$PI_HOST"
echo "  2. Edit config: nano $INKYPI_PLUGINS_DIR/$PLUGIN_NAME/config.yaml"
echo "     (or use the .env file if you copied it)"
echo "  3. Test the plugin:"
echo "     cd $INKYPI_PLUGINS_DIR/$PLUGIN_NAME"
echo "     python3 test_apis.py"
echo "  4. Enable plugin in InkyPi web interface"
echo "  5. Restart InkyPi service if needed"
echo ""
echo -e "${YELLOW}Optional: Test APIs now?${NC}"
read -p "Run test_apis.py on the Pi? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Running API tests...${NC}"
    ssh $SSH_OPTS "$PI_USER@$PI_HOST" "cd $INKYPI_PLUGINS_DIR/$PLUGIN_NAME && python3 test_apis.py"
fi

echo ""
echo -e "${GREEN}Done!${NC}"
