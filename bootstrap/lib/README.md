# Shared deployment library

`deploy.py` validates manifests, composes capability groups, plans destination
files, rejects conflicting user files and symlink traversal, and applies explicit
deployments. Manual bootstrap, Calamares and live-image skeleton creation all use
this implementation. Root account creation, partitioning and user passwords are
outside this library; Calamares owns those installer jobs.
