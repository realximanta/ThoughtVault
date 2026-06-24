# NxCreate Integration

This folder documents the Telegram → GitHub integration used by ThoughtVault.

## Purpose

Allow Telegram commands to trigger GitHub Actions workflows instantly.

## Environment Variables

```env
BOT_TOKEN=

GITHUB_PAT=

GITHUB_OWNER=

GITHUB_REPO=

GITHUB_WORKFLOW=

ALLOWED_USER_ID=
```

## Command

### /force

```
const OWNER_ID = Your Chat Id Here;

bot.command("force", async (ctx) => {
    if (!ctx.from || ctx.from.id !== OWNER_ID) {
        return ctx.reply("⛔ Unauthorized");
    }

    try {
        const response = await axios.post(
            `https://api.github.com/repos/${process.env.GITHUB_OWNER}/${process.env.GITHUB_REPO}/actions/workflows/${process.env.GITHUB_WORKFLOW}/dispatches`,
            {
                ref: "main"
            },
            {
                headers: {
                    Authorization: `Bearer ${process.env.GITHUB_PAT}`,
                    Accept: "application/vnd.github+json"
                }
            }
        );

        return ctx.reply(
            "🚀 ThoughtVault sync started successfully."
        );

    } catch (err) {
        return ctx.reply(
            `❌ Error triggering workflow.\n\n${err.message}`
        );
    }
});
```

Triggers the configured GitHub Actions workflow using GitHub REST API.

Flow:

Telegram
↓
NxCreate Bot
↓
GitHub API
↓
workflow_dispatch
↓
GitHub Actions
↓
ThoughtVault Sync

## Security

Only the configured owner ID can execute `/force`.

Unauthorized users are ignored.

## Example

```txt
/force
```

Response:

```txt
🚀 ThoughtVault sync started successfully.
```

## Project

ThoughtVault v2.0.0
NxCreate Integration Layer
```
