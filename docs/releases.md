# Releases and versioning

Download images from [GitHub Releases](https://github.com/abstring/ABSLinux/releases).
ISOs and VM disks belong in release assets or ignored build output, not Git history.

## Version policy

`VERSION` is the single source for the ABS release version; Git tags add a `v`
prefix. This is the ABS integration version, independent of Debian's version.
Keep Debian's `/etc/os-release` unchanged.

- `0.1.0-alpha.1`: first VM-tested installer preview.
- Increment the alpha number (`0.1.0-alpha.2`, `.3`, ...) for every subsequent
  published preview, including rebuilt images with changed Debian packages.
- Use `0.1.0-beta.1` once planned scope is complete and hardware validation is
  underway; use `0.1.0-rc.1` when release acceptance checks are complete.
- Publish `0.1.0` when the documented release criteria pass. Increment patch for
  fixes, minor for new compatible functionality, and major for breaking changes
  after 1.0. Before 1.0, document breaking changes explicitly in minor releases.
- Update `VERSION` before building the next candidate. Never replace a published
  ISO with different bytes under the same version/tag; issue a new version.

`build/build-iso.sh` uses VERSION for the image name:
`abs-linux-0.1.0-alpha.1-amd64.hybrid.iso`. Checksums use basenames so users can run
`sha256sum -c SHA256SUMS` in their download directory.

## Publication checklist

1. Set the next version, build and validate it. Record checksum, Debian/kernel
   versions, source commit, test results and known limitations.
2. Commit source and evidence summary. Keep secrets, build trees and VM fixture
   accounts out of Git and release assets.
3. Tag the committed source as `v<VERSION>` and push commits and the tag.
4. Create the GitHub release with the versioned ISO, `SHA256SUMS` and clear notes.
   Mark alpha/beta/rc versions as prereleases. Keep the README download link aimed
   at `/releases`, since `/releases/latest` can omit prereleases.
5. Verify the published assets and checksum. Retain the original tested ISO;
   filename-only changes do not require rebuilding it.

## First preview provenance

The `v0.1.0-alpha.1` asset is the unchanged ISO tested in
[VM validation](vm-validation.md), renamed for publication. Its image payload
corresponds to commit `2233bab`; the release tag additionally includes VERSION,
automatic build naming and release documentation. Those additions do not change
the tested image payload. Subsequent images should be built with their versioned
filename directly through the build script.
