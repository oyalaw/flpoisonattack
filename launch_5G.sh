#!/usr/bin/env bash
set -Eeuo pipefail

HOTSPOT_PROFILE="${HOTSPOT_PROFILE:-fl-hotspot}"
HOTSPOT_IFACE="${HOTSPOT_IFACE:-wlo1}"
HOTSPOT_SSID="${HOTSPOT_SSID:-FL-Hotspot}"
HOTSPOT_PASSWORD="${HOTSPOT_PASSWORD:-12345678}"

log() {
    echo "==> $*"
}

warn() {
    echo "WARNING: $*" >&2
}

die() {
    echo "ERROR: $*" >&2
    exit 1
}

iface_exists() {
    ip link show "$1" >/dev/null 2>&1
}

nm_profile_exists() {
    nmcli -t -f NAME connection show 2>/dev/null | grep -Fxq "$1"
}

ensure_prereqs() {
    command -v ip >/dev/null 2>&1 || die "ip command is not installed"
    command -v nmcli >/dev/null 2>&1 || die "nmcli is not installed"
}

ensure_hotspot_profile() {
    if nm_profile_exists "$HOTSPOT_PROFILE"; then
        return
    fi

    log "Creating hotspot profile $HOTSPOT_PROFILE"

    nmcli connection add \
        type wifi \
        ifname "$HOTSPOT_IFACE" \
        con-name "$HOTSPOT_PROFILE" \
        autoconnect no \
        ssid "$HOTSPOT_SSID" >/dev/null

    nmcli connection modify "$HOTSPOT_PROFILE" 802-11-wireless.mode ap
    nmcli connection modify "$HOTSPOT_PROFILE" 802-11-wireless.band bg
    nmcli connection modify "$HOTSPOT_PROFILE" ipv4.method shared
    nmcli connection modify "$HOTSPOT_PROFILE" wifi-sec.key-mgmt wpa-psk
    nmcli connection modify "$HOTSPOT_PROFILE" wifi-sec.psk "$HOTSPOT_PASSWORD"
}

restart_hotspot() {
    if ! iface_exists "$HOTSPOT_IFACE"; then
        die "Hotspot interface $HOTSPOT_IFACE not found"
    fi

    ensure_hotspot_profile

    log "Restarting hotspot profile $HOTSPOT_PROFILE on $HOTSPOT_IFACE"

    nmcli connection down "$HOTSPOT_PROFILE" >/dev/null 2>&1 || true
    nmcli connection up "$HOTSPOT_PROFILE" >/dev/null

    sleep 2

    if ip a show "$HOTSPOT_IFACE" | grep -q "10.42.0.1/"; then
        echo "Hotspot started successfully"
    else
        warn "Hotspot started, but expected 10.42.0.1 was not detected yet"
    fi
}

print_summary() {
    echo
    echo "===== HOTSPOT STARTED ====="
    echo "Hotspot profile:  $HOTSPOT_PROFILE"
    echo "Hotspot iface:    $HOTSPOT_IFACE"
    echo "Hotspot SSID:     $HOTSPOT_SSID"
    echo
    echo "Check hotspot IP: ip a show $HOTSPOT_IFACE"
    echo
}

main() {
    ensure_prereqs
    restart_hotspot
    print_summary
}

main "$@"
