---
name: release-setup
description: Set up automated cross-platform binary releases for a Go project
---

# Release Setup

Set up automated binary releases for a Go CLI project. Every push to main builds and publishes cross-platform binaries. No tags, no manual release steps.

## Prerequisites

Before starting, read the project to determine:
- **Binary name**: from Makefile, go.mod module path, or main package
- **GitHub owner/repo**: from `git remote get-url origin`
- **License**: from LICENSE file
- **Description**: from README.md first line or go.mod comment

Ask the user which platforms to target. Default: macOS ARM, Linux x86_64, Linux ARM. Optional: Windows x86_64.

## Steps

Work through each step, implementing immediately. Show what you're creating and why.

---

### 1. Version variable

The version string format is: `YYYY-MM-DD HH:MM <branch> <short-sha> <dev|release>`

Examples:
- Local build: `2026-04-10 14:22 main fa431a dev`
- CI release: `2026-04-10 14:22 main fa431a release`

**In the source code**, find where the version is defined. Replace any hardcoded version string with a `var` that defaults to `"dev"` and is set at build time via ldflags:

For Go:
```go
// version is set at build time via -ldflags "-X main.version=..."
var version = "dev"
```

For Rust (in build.rs + env!):
```rust
let version = option_env!("BUILD_VERSION").unwrap_or("dev");
```

**In the Makefile** (or equivalent build config), set VERSION and pass it via ldflags:

For Go:
```makefile
VERSION  = $(shell date -u +'%Y-%m-%d %H:%M') $(shell git rev-parse --abbrev-ref HEAD) $(shell git rev-parse --short HEAD) dev
GOFLAGS  = -trimpath -ldflags="-s -w -X 'main.version=$(VERSION)'"
```

If the project has an existing hardcoded version constant, remove it. If there's a `make release` target that manages tags, remove it.

---

### 2. GitHub Actions workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod

      - name: Build binaries
        run: |
          SHA=$(git rev-parse --short HEAD)
          DATE=$(TZ=UTC date +'%Y-%m-%d %H:%M')
          VERSION="${DATE} main ${SHA} release"
          LDFLAGS="-s -w -X 'main.version=${VERSION}'"
          GOOS=darwin  GOARCH=arm64 go build -trimpath -ldflags="$LDFLAGS" -o dist/<BINARY>-darwin-arm64  .
          GOOS=linux   GOARCH=amd64 go build -trimpath -ldflags="$LDFLAGS" -o dist/<BINARY>-linux-amd64  .
          GOOS=linux   GOARCH=arm64 go build -trimpath -ldflags="$LDFLAGS" -o dist/<BINARY>-linux-arm64  .

      - name: Create or update release
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          gh release delete latest --yes 2>/dev/null || true
          git push origin :refs/tags/latest 2>/dev/null || true
          gh release create latest \
            dist/<BINARY>-darwin-arm64 \
            dist/<BINARY>-linux-amd64 \
            dist/<BINARY>-linux-arm64 \
            --title "Latest" \
            --notes "Built from main at $(git rev-parse --short HEAD)" \
            --latest
```

Replace `<BINARY>` with the actual binary name. If Windows is requested, add:
```yaml
          GOOS=windows GOARCH=amd64 go build -trimpath -ldflags="$LDFLAGS" -o dist/<BINARY>-windows-amd64.exe .
```
and include it in the `gh release create` assets list.

Adapt the setup step for non-Go projects (e.g. `actions/setup-node`, `rustup`, etc.).

---

### 3. Homebrew formula

Check if the user has a homebrew tap repo. Look for `../homebrew-tap` or ask. If they have one, create a formula.

Create `Formula/<binary>.rb` in the tap repo:

```ruby
class <BinaryClass> < Formula
  desc "<project description>"
  homepage "https://github.com/<owner>/<repo>"
  version "latest"
  license "<license>"

  on_macos do
    on_arm do
      url "https://github.com/<owner>/<repo>/releases/download/latest/<binary>-darwin-arm64"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/<owner>/<repo>/releases/download/latest/<binary>-linux-arm64"
    end
    on_intel do
      url "https://github.com/<owner>/<repo>/releases/download/latest/<binary>-linux-amd64"
    end
  end

  def install
    bin.install Dir.glob("<binary>-*").first => "<binary>"
  end

  test do
    assert_match "<binary>", shell_output("#{bin}/<binary> --version")
  end
end
```

Commit and push the formula to the tap repo.

---

### 4. README install section

Add or update the Install section in the project's README.md. Place it near the top, after the project description and any quick-start examples:

```markdown
## Install

### Homebrew (macOS/Linux)

\`\`\`sh
$ brew install <owner>/tap/<binary>
\`\`\`

### Download binary

Download the latest binary for your platform:

\`\`\`sh
# macOS (Apple Silicon)
$ curl -Lo <binary> https://github.com/<owner>/<repo>/releases/latest/download/<binary>-darwin-arm64

# Linux (x86_64)
$ curl -Lo <binary> https://github.com/<owner>/<repo>/releases/latest/download/<binary>-linux-amd64

# Linux (ARM)
$ curl -Lo <binary> https://github.com/<owner>/<repo>/releases/latest/download/<binary>-linux-arm64
\`\`\`

Then make it executable and move it to your PATH:

\`\`\`sh
$ chmod +x <binary>
$ sudo mv <binary> /usr/local/bin/
\`\`\`

### From source

Requires Go 1.21+:

\`\`\`sh
$ go install <module>@latest
\`\`\`
```

If Windows was included, add a Windows section to the download instructions.

Skip the Homebrew subsection if no tap was set up. Skip "From source" if not applicable.

---

### 5. Verify

After implementing all steps:
1. Run `make build` and check `<binary> --version` shows the dev version string
2. Commit and push to main
3. Watch `gh run watch` to confirm the workflow succeeds
4. Test `curl -Lo <binary> https://github.com/<owner>/<repo>/releases/latest/download/<binary>-<platform>` and verify the downloaded binary runs and shows the release version string
5. If Homebrew was set up, test `brew install <owner>/tap/<binary>`

## Guidelines

- **No tags.** Version comes from build-time date + git sha. No semver, no tag management.
- **Rolling release.** The `latest` GitHub release is replaced on every push to main.
- **Bare binaries.** Release assets are standalone executables, not zips or tars.
- **Asset naming.** `<binary>-<os>-<arch>` (e.g. `myapp-linux-amd64`). Windows gets `.exe` suffix.
- **Adapt to the language.** The examples are Go-centric but the pattern works for any compiled language. Adjust the build commands, version injection mechanism, and CI setup step accordingly.
