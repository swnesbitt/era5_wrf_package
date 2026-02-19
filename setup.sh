#!/bin/bash
# =============================================================================
# setup.sh - One-time setup for ERA5-WRF package
#
# Creates symlinks in the package directory pointing to your local WRF and WPS
# installations. Run this once before using wrf_driver_era5.sh.
#
# Environment variables (all have defaults):
#   WRF_DIR     - Path to WRF em_real run directory
#   WPS_DIR     - Path to WPS installation directory
#   GEO_EM_FILE - Path to geo_em.d01.nc domain file
#
# Usage:
#   bash setup.sh
#   WRF_DIR=/my/wrf/path WPS_DIR=/my/wps/path GEO_EM_FILE=/my/geo_em.nc bash setup.sh
# =============================================================================

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Defaults matching snesbitt's installation — override via env vars
WRF_DIR="${WRF_DIR:-/data/accp/a/snesbitt/wrf47/WRFV4.7.1/test/em_real}"
WPS_DIR="${WPS_DIR:-/data/accp/a/snesbitt/wrf47/WPS-4.6.0}"
GEO_EM_FILE="${GEO_EM_FILE:-/data/accp/a/snesbitt/wrf/domains/sa_3km_3/geo_em.d01.nc}"

echo "ERA5-WRF Package Setup"
echo "======================"
echo "  PACKAGE_DIR  : $PACKAGE_DIR"
echo "  WRF_DIR      : $WRF_DIR"
echo "  WPS_DIR      : $WPS_DIR"
echo "  GEO_EM_FILE  : $GEO_EM_FILE"
echo ""

# Validate that target paths exist
ERRORS=0

if [ ! -d "$WRF_DIR" ]; then
    echo "ERROR: WRF_DIR does not exist: $WRF_DIR"
    ERRORS=$((ERRORS + 1))
fi

if [ ! -d "$WPS_DIR" ]; then
    echo "ERROR: WPS_DIR does not exist: $WPS_DIR"
    ERRORS=$((ERRORS + 1))
fi

if [ ! -f "$GEO_EM_FILE" ]; then
    echo "ERROR: GEO_EM_FILE does not exist: $GEO_EM_FILE"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "Setup failed. Fix the above errors and re-run setup.sh."
    exit 1
fi

# Create symlinks (overwrite if already exist)
ln -sfn "$WRF_DIR" "$PACKAGE_DIR/wrf"
ln -sfn "$WPS_DIR" "$PACKAGE_DIR/wps"

# Write GEO_EM_FILE path to a config file so the Python script can read it
cat > "$PACKAGE_DIR/.wrf_config" << EOF
GEO_EM_FILE=$GEO_EM_FILE
EOF

echo "Symlinks created:"
echo "  $(ls -la "$PACKAGE_DIR/wrf")"
echo "  $(ls -la "$PACKAGE_DIR/wps")"
echo ""
echo "Domain file:"
echo "  GEO_EM_FILE=$GEO_EM_FILE (saved to .wrf_config)"
echo ""
echo "Setup complete. You can now submit jobs with:"
echo "  sbatch wrf_driver_era5.sh <YYYYMMDDHH> <HOURS> <OUTPUT_DIR>"
