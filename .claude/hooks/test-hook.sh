#\!/bin/bash
# Ultra minimal hook - just log and exit

echo "Hook called at $(date)" >> /tmp/hook-minimal.log

exit 0
EOF < /dev/null