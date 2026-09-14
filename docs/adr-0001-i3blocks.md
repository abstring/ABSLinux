# ADR 0001: Retain i3bar/i3blocks for the installer foundation

Status: accepted, 2026-09-14.

The roadmap proposed Polybar, but live inspection found a working i3bar/i3blocks
desktop on the primary reference system. Moving to Polybar during installer
bring-up would change two major subsystems at once without an observed need.

Use Debian i3bar/i3blocks now. Port the useful status categories and click actions
into small portable scripts. Generate only capability-dependent battery and
Bluetooth blocks at bar startup. Keep the common bar configuration user-editable.
No Polybar migration is scheduled or required; a later proposal must demonstrate
a concrete benefit and preserve existing behavior.

The first battery block shows each battery independently. The reference BatteryBar
wrapper depends on a separate working checkout, so visual BatteryBar parity is
not claimed. LCARS and complex battery visualizations remain separately scoped
integrations. The terminal and new-image display manager are intentional choices:
Kitty and LightDM keep the fresh desktop small while manual deployments retain
their existing display manager. Neither is presented as a copy of Defuser's stack.
