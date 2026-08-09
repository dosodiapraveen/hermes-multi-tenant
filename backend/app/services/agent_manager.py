"""
Hermes Agent Manager
Routes all user messages through `hermes chat --query --in {profile_dir}`
instead of direct AI API calls. Each user gets an isolated Hermes profile.
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Constants
PROFILES_ROOT = Path("/opt/hermes/profiles")
HERMES_BIN = "/usr/local/bin/hermes"
HERMES_PYTHON = None
HERMES_TIMEOUT = 60  # seconds per query


async def hermes_profile_chat(
    user_id: str,
    message: str,
    profile_dir: Optional[str] = None,
    timeout: int = HERMES_TIMEOUT,
) -> str:
    """
    Route a user message through their isolated Hermes profile.

    Runs: hermes chat --query "<message>" --in <profile_dir> --no-restore-cwd -Q

    Args:
        user_id: The UUID of the user (used to find profile dir)
        message: The user's message text
        profile_dir: Optional explicit profile directory path.
                     If not provided, derived from PROFILES_ROOT / user_id
        timeout: Max seconds to wait for the Hermes subprocess

    Returns:
        The response text from the Hermes agent

    Raises:
        FileNotFoundError: If the profile directory doesn't exist
        TimeoutError: If the Hermes process times out
        RuntimeError: If Hermes CLI returns a non-zero exit code
    """
    if profile_dir:
        profile_path = Path(profile_dir)
    else:
        profile_path = PROFILES_ROOT / user_id

    if not profile_path.exists() or not profile_path.is_dir():
        raise FileNotFoundError(
            f"Hermes profile not found for user {user_id}: {profile_path}"
        )

    # Build the command
    cmd = [HERMES_BIN, "chat",
        "--query", message,
        "--in", str(profile_path),
        "--no-restore-cwd", "-Q",
    ]

    logger.info(
        "Running Hermes for user %s: %s --query <len=%d> --in %s",
        user_id, HERMES_BIN, len(message), profile_path,
    )

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={
                **os.environ,
                "HERMES_HOME": os.environ.get("HERMES_HOME", "/root/.hermes"),
            },
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise TimeoutError(
                f"Hermes agent timed out after {timeout}s for user {user_id}"
            )

        if proc.returncode != 0:
            stderr_text = stderr.decode("utf-8", errors="replace").strip()
            stdout_text = stdout.decode("utf-8", errors="replace").strip()
            error_msg = (
                f"Hermes exited with code {proc.returncode} for user {user_id}"
            )
            if stderr_text:
                error_msg += f"\nstderr: {stderr_text[:500]}"
            if stdout_text:
                error_msg += f"\nstdout: {stdout_text[:500]}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        response = stdout.decode("utf-8", errors="replace").strip()
        logger.info(
            "Hermes response for user %s: %d chars",
            user_id, len(response),
        )
        return response

    except FileNotFoundError:
        raise
    except TimeoutError:
        raise
    except RuntimeError:
        raise
    except Exception as e:
        logger.error(
            "Unexpected error running Hermes for user %s: %s",
            user_id, str(e),
        )
        raise RuntimeError(f"Hermes agent error: {e}") from e


async def hermes_profile_chat_with_fallback(
    user_id: str,
    message: str,
    profile_dir: Optional[str] = None,
    timeout: int = HERMES_TIMEOUT,
) -> str:
    """
    Run Hermes with a fallback: if the command fails, return a graceful
    error message instead of propagating the exception.

    Returns:
        The response text, or a fallback message on failure.
    """
    try:
        return await hermes_profile_chat(
            user_id=user_id,
            message=message,
            profile_dir=profile_dir,
            timeout=timeout,
        )
    except FileNotFoundError:
        logger.warning("Profile not found for user %s; returning fallback", user_id)
        return "Your agent profile is not set up yet. Please contact support."
    except TimeoutError:
        logger.warning("Hermes timed out for user %s", user_id)
        return "Your agent is taking too long to respond. Please try again."
    except RuntimeError as e:
        logger.error("Hermes runtime error for user %s: %s", user_id, e)
        return "Sorry, I encountered an error processing your request."
    except Exception as e:
        logger.error("Unexpected error for user %s: %s", user_id, e)
        return "Service temporarily unavailable. Please try again later."


def get_user_profile_dir(user_id: str) -> Path:
    """Get the expected profile directory path for a user."""
    return PROFILES_ROOT / user_id


def profile_exists(user_id: str) -> bool:
    """Check if a user's Hermes profile directory exists on disk."""
    return get_user_profile_dir(user_id).exists()


async def write_user_skill(
    user_id: str,
    skill_name: str,
    content: str,
    profile_dir: Optional[str] = None,
) -> str:
    """
    Write a skill file to a user's Hermes profile.

    Args:
        user_id: The user's UUID
        skill_name: The skill name (e.g. 'user-preferences.md' or 'custom-instructions.md')
        content: The full markdown content of the skill
        profile_dir: Optional explicit profile directory

    Returns:
        The path to the written skill file
    """
    if profile_dir:
        profile_path = Path(profile_dir)
    else:
        profile_path = PROFILES_ROOT / user_id

    skills_dir = profile_path / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    skill_path = skills_dir / skill_name
    loop = asyncio.get_running_loop()

    def _write():
        with open(skill_path, "w") as f:
            f.write(content)
        os.chmod(skill_path, 0o644)

    await loop.run_in_executor(None, _write)
    logger.info("Wrote skill %s for user %s at %s", skill_name, user_id, skill_path)
    return str(skill_path)


async def update_user_model_config(
    user_id: str,
    primary_model: Optional[str] = None,
    backup_model: Optional[str] = None,
    profile_dir: Optional[str] = None,
) -> dict:
    """
    Update the model configuration in a user's Hermes profile config.yaml.

    This updates the on-disk config to match the database override.

    Returns:
        Dict with 'primary_model' and 'backup_model' showing what was set.
    """
    if profile_dir:
        profile_path = Path(profile_dir)
    else:
        profile_path = PROFILES_ROOT / user_id

    config_path = profile_path / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"No config.yaml for user {user_id}")

    import yaml

    loop = asyncio.get_running_loop()

    def _update():
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}

        if "model" not in config:
            config["model"] = {}

        result = {}

        if primary_model:
            config["model"]["model"] = primary_model
            config["model"]["provider"] = _infer_provider(primary_model)
            result["primary_model"] = primary_model

        if backup_model:
            if "backup" not in config["model"]:
                config["model"]["backup"] = {}
            config["model"]["backup"]["model"] = backup_model
            config["model"]["backup"]["provider"] = _infer_provider(backup_model)
            result["backup_model"] = backup_model

        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        return result

    return await loop.run_in_executor(None, _update)


def _infer_provider(model: str) -> str:
    """Infer the provider from a model string."""
    if model.startswith("claude"):
        return "anthropic"
    if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        return "openai"
    if "fireworks" in model or model.startswith("accounts/"):
        return "fireworks"
    if model.startswith("gemini"):
        return "google"
    return "fireworks"  # default


async def write_global_skill_template(
    skill_name: str,
    content: str,
    user_ids: Optional[list[str]] = None,
) -> list[dict]:
    """
    Write a skill template to all users' profiles (or specified subset).

    Args:
        skill_name: The skill filename (e.g. 'global-instructions.md')
        content: The markdown content
        user_ids: Optional list of user IDs to write to. If None,
                  writes to all profiles found on disk.

    Returns:
        List of dicts with user_id and status for each write attempt.
    """
    results = []

    if user_ids:
        target_users = user_ids
    else:
        # Discover all profiles on disk
        if not PROFILES_ROOT.exists():
            return results
        loop = asyncio.get_running_loop()

        def _list_dirs():
            return [
                d.name for d in PROFILES_ROOT.iterdir()
                if d.is_dir() and (d / "config.yaml").exists()
            ]

        target_users = await loop.run_in_executor(None, _list_dirs)

    for uid in target_users:
        try:
            path = await write_user_skill(uid, skill_name, content)
            results.append({"user_id": uid, "status": "ok", "path": path})
        except Exception as e:
            logger.error("Failed to write skill %s for user %s: %s", skill_name, uid, e)
            results.append({"user_id": uid, "status": "failed", "error": str(e)})

    return results
