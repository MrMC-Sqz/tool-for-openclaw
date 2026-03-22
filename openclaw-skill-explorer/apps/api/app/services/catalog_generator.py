from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BLUEPRINTS_PATH = PROJECT_ROOT / "scripts" / "data" / "public_catalog_blueprints.json"


def load_catalog_blueprints(path: Path | None = None) -> dict:
    blueprint_path = path or DEFAULT_BLUEPRINTS_PATH
    with blueprint_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("Catalog blueprints must be an object.")
    return payload


def generate_public_catalog(
    count: int = 120,
    path: Path | None = None,
) -> list[dict]:
    blueprints = load_catalog_blueprints(path)
    categories = blueprints.get("categories", [])
    roles = blueprints.get("roles", [])
    install_methods = blueprints.get("install_methods", ["registry"])

    if not isinstance(categories, list) or not isinstance(roles, list):
        raise ValueError("Blueprint categories and roles must be lists.")

    generated_items: list[dict] = []
    base_time = datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc)

    for category_index, category in enumerate(categories):
        category_name = str(category.get("name") or "").strip()
        category_slug = str(category.get("slug") or category_name.lower()).strip()
        category_description = str(category.get("description_prefix") or "").strip()
        category_tags = [str(tag).strip().lower() for tag in category.get("tags", []) if str(tag).strip()]
        category_channels = [
            str(channel).strip().lower() for channel in category.get("channels", []) if str(channel).strip()
        ]
        category_artifacts = [
            str(artifact).strip().lower() for artifact in category.get("artifacts", []) if str(artifact).strip()
        ]

        for role_index, role in enumerate(roles):
            role_name = str(role.get("name") or "").strip()
            role_slug = str(role.get("slug") or role_name.lower()).strip()
            role_focus = str(role.get("focus") or "").strip()
            role_tags = [str(tag).strip().lower() for tag in role.get("tags", []) if str(tag).strip()]
            role_channel = category_channels[role_index % len(category_channels)] if category_channels else ""
            role_artifact = (
                category_artifacts[(category_index + role_index) % len(category_artifacts)]
                if category_artifacts
                else "records"
            )

            combined_tags = []
            for tag in [category_slug, role_slug, "automation", role_channel, role_artifact, *category_tags, *role_tags]:
                normalized = str(tag or "").strip().lower()
                if normalized and normalized not in combined_tags:
                    combined_tags.append(normalized)

            sequence = len(generated_items)
            updated_at = base_time + timedelta(hours=sequence * 4)
            stars = 60 + ((category_index * 17 + role_index * 11) % 220)
            install_method = install_methods[sequence % len(install_methods)]
            repo_name = f"{category_slug}-{role_slug}"
            generated_items.append(
                {
                    "name": f"OpenClaw {category_name} {role_name}",
                    "repo_url": f"https://github.com/openclaw-public/{repo_name}",
                    "category": category_slug,
                    "description": (
                        f"{category_description} {role_focus} across {role_channel or 'team'} workflows "
                        f"with {role_artifact} handling and repeatable automation steps."
                    ).strip(),
                    "readme_summary": (
                        f"{category_name} automation skill focused on {role_focus.lower()} "
                        f"for {role_channel or 'team'} workflows and {role_artifact} operations."
                    ),
                    "tags": combined_tags,
                    "stars": stars,
                    "last_repo_updated_at": updated_at.isoformat().replace("+00:00", "Z"),
                    "author": "OpenClaw Public Catalog",
                    "install_method": install_method,
                    "offline_only": True,
                }
            )
            if len(generated_items) >= count:
                return generated_items

    return generated_items[:count]
