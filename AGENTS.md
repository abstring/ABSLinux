# Repository instructions

Run all Git, GitHub CLI, and repository-related commands for this repository as the `abstring` user. For example, use `sudo -u abstring -H gh ...` when the current process is not already running as `abstring`.

## Work on issues

When asked to **work on issues**, use this workflow:

1. Pull the most recent changes from the repository. Preserve local work and use a safe, non-destructive update method; do not discard or overwrite unrelated changes.
2. Gather all open GitHub issues and inspect enough repository context to understand them.
3. Determine which issues are ready to be handled, including which can sensibly be merged into one iteration. Compile a concrete list of planned actions, report that plan to the user, and wait for explicit authorization before making issue-related changes.
4. After authorization, take action according to the approved plan. If new information requires a material change in scope, report it and obtain authorization before proceeding.
5. Produce a detailed report of the work and validation. Update existing issues with their resolutions and close only those that are complete. If additional problems are discovered but are not ready or in scope for the current iteration, create new GitHub issues for them with enough detail for later work.
6. Update the repository documentation or other tracked state needed to keep it current, then commit and push the completed, validated changes. Stage only the intended paths and leave unrelated files untouched.

Authorization at step 3 covers the approved actions in steps 4 through 6, including resolution comments, closing completed issues, creating follow-up issues for newly discovered out-of-scope work, and committing and pushing the approved repository changes.

## ABSLinux validation and releases

For installer or image changes, build a uniquely versioned candidate, test live boot
and installation in disposable QEMU disks, then boot without the ISO. Inspect actual
QEMU framebuffer screenshots for visual work. Never attach host disks to test VMs.
Separate VM evidence from real-hardware confirmation; close only verified issues.
Update VERSION and follow docs/releases.md when publishing an approved iteration.
Preserve existing user configuration when documenting or implementing upgrades.
