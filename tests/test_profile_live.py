"""Offline regression coverage for the additive GitHub profile inventory."""
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
from unittest.mock import patch

from scripts import generate_profile_live as profile


def public_repo(name, *, description="", size=1):
    return {
        "id": name,
        "name": name,
        "description": description,
        "size": size,
        "private": False,
        "visibility": "public",
        "pushed_at": "2026-11-21T16:00:00Z",
    }


class PublicRepositoryCatalogTests(unittest.TestCase):
    def test_new_engine_and_games_have_explicit_category(self):
        for name in (
            "ARKYVON",
            "Global-Chess-Online-PVP-",
            "Global-Carrom-Online-PVP-",
            "Global-Brain-Iq-Train-Puzzle",
        ):
            self.assertEqual(profile.catalog_category(public_repo(name)), "GAME / ENGINE")

    def test_known_new_projects_are_in_catalog(self):
        names = [
            "ARKYVON",
            "Global-Chess-Online-PVP-",
            "OpenXdrive",
            "Unlimited-Auto-Cut-Clipper-Tool",
        ]
        rendered = profile.render_repo_catalog([public_repo(name) for name in names])
        for name in names:
            self.assertIn(name, rendered)
        self.assertIn("Explore all 4 public repositories", rendered)

    def test_private_repos_never_appear_even_if_passed(self):
        private = {
            **public_repo("private-finance-repo"),
            "private": True,
            "visibility": "private",
        }
        rendered = profile.render_repo_catalog([public_repo("ARKYVON"), private])
        self.assertNotIn("private-finance-repo", rendered)
        self.assertIn("Explore all 1 public repositories", rendered)

    def test_public_directory_escapes_untrusted_description(self):
        rendered = profile.render_repo_catalog([
            public_repo("example", description='<script>alert("x")</script>')
        ])
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_no_entries_is_rejected(self):
        with self.assertRaises(ValueError):
            profile.render_repo_catalog([])


class GeneratedMarkerTests(unittest.TestCase):
    def test_only_machine_owned_span_changes(self):
        old = "header\n<!-- START -->\nold\n<!-- END -->\nfooter\n"
        updated = profile.replace_owned_block(old, "<!-- START -->", "<!-- END -->", "new")
        self.assertTrue(updated.startswith("header\n"))
        self.assertTrue(updated.endswith("footer\n"))
        self.assertNotIn("old", updated)
        self.assertIn("new", updated)

    def test_missing_or_duplicate_markers_fail_closed(self):
        with self.assertRaises(ValueError):
            profile.replace_owned_block("no markers", "<!-- START -->", "<!-- END -->", "new")
        with self.assertRaises(ValueError):
            profile.replace_owned_block("<!-- END --><!-- START -->", "<!-- START -->", "<!-- END -->", "new")

    def test_catalog_update_is_idempotent_and_does_not_rewrite_manual_sections(self):
        readme = (
            "# Original hero (preserve)\n"
            f"{profile.COUNT_START}\n<b>49</b>\n{profile.COUNT_END}\n"
            "## Product section (preserve)\n"
            f"{profile.CATALOG_START}\nold catalog\n{profile.CATALOG_END}\n"
            "## Contribution city (preserve)\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "README.md"
            p.write_text(readme, encoding="utf-8")
            sample = [public_repo("ARKYVON")]
            profile.update_readme_catalog(sample, readme_path=p)
            first = p.read_text(encoding="utf-8")
            profile.update_readme_catalog(sample, readme_path=p)
            second = p.read_text(encoding="utf-8")
        self.assertEqual(first, second)
        self.assertIn("# Original hero (preserve)", first)
        self.assertIn("## Product section (preserve)", first)
        self.assertIn("## Contribution city (preserve)", first)
        self.assertIn("<b>12</b>", first)  # 1 public + 11 audited private

    def test_api_empty_inventory_does_not_replace_assets(self):
        with patch.object(profile, "request_json", return_value=[]):
            with self.assertRaises(RuntimeError):
                profile.fetch_public_repos()

    def test_repo_pagination_and_dedupe(self):
        first = [public_repo(f"test-{i:03d}") for i in range(100)]
        second = [public_repo("test-050"), public_repo("test-100")]
        with patch.object(profile, "request_json", side_effect=[first, second]):
            result = profile.fetch_public_repos()
        self.assertEqual(len(result), 101)

    def test_curated_stages_separate_build_testing_and_shipped(self):
        heartbeat = {item["repo"]: item["status"] for item in profile.CONFIG["heartbeat_products"]}
        self.assertEqual(heartbeat["ARKYVON"], "BUILDING")
        self.assertEqual(heartbeat["Global-Chess-Online-PVP-"], "BUILDING")
        self.assertEqual(heartbeat["OpenXdrive"], "TESTING")
        self.assertEqual(heartbeat["Unlimited-Auto-Cut-Clipper-Tool"], "TESTING")
        self.assertEqual(heartbeat["FinCo-pilot"], "SHIPPED")
        self.assertEqual(heartbeat["Toolshub"], "SHIPPED")
        self.assertEqual(profile.CONFIG["private_count_verified"], 11)



class CurrentFocusRenderingTests(unittest.TestCase):
    def test_terminal_does_not_claim_old_flagships_are_current_builds(self):
        svg = profile.generate_terminal(47)
        self.assertIn("ARKYVON Engine", svg)
        self.assertIn("Global Chess", svg)
        self.assertNotIn("HARDENING", svg)
        self.assertNotIn("ToolsLab LLMs", svg)

    def test_heartbeat_rendering_has_testing_and_shipped_states(self):
        svg = profile.generate_heartbeat({})
        self.assertIn("TESTING", svg)
        self.assertIn("SHIPPED", svg)
        self.assertIn("BUILDING", svg)
        self.assertNotIn(">RESEARCH</text>", svg)

    def test_timeline_all_stages_fit_without_overlay(self):
        svg = profile.generate_timeline({})
        self.assertIn('viewBox="0 0 900 542"', svg)
        self.assertIn("ARKYVON", svg)
        self.assertIn("Chess", svg)
        self.assertIn("ToolsLab", svg)
        self.assertIn("FinCo", svg)
        self.assertIn("LiveClip", svg)
        self.assertIn("OpenXdrive", svg)

    def test_editorial_publication_urls_are_public_and_named(self):
        publications = profile.CONFIG["editorial_publications"]
        self.assertTrue(any(item["name"] == "The Paisa Journal" and
                            item["url"] == "https://thepaisajournal.blogspot.com/"
                            for item in publications))
        self.assertTrue(any(item["name"] == "FinCalc India Blog" for item in publications))




class ProfileAssetIntegrationTests(unittest.TestCase):
    def test_game_and_creator_clusters_use_specific_classification(self):
        for name in ("ARKYVON", "Global-Chess-Online-PVP-", "Global-Carrom-Online-PVP-",
                     "Global-Brain-Iq-Train-Puzzle"):
            self.assertEqual(profile.classify_repo(public_repo(name)), "GAME")
        for name in ("Unlimited-Auto-Cut-Clipper-Tool", "Satzzxzxx-Labs"):
            self.assertEqual(profile.classify_repo(public_repo(name)), "CREATOR")
        self.assertEqual(profile.classify_repo(public_repo("OpenXdrive")), "SYSTEMS")

    def test_new_static_svg_assets_are_well_formed(self):
        for name in ("three-path-workflow-v3.svg", "building-now-v2.svg",
                     "shipped-products-v2.svg", "repo-constellation-live.svg",
                     "shipping-timeline-live.svg", "terminal-boot-live.svg",
                     "product-heartbeat-live.svg", "profile-hero-v2.svg"):
            with self.subTest(name=name):
                xml_text = (profile.ROOT / "assets" / name).read_text(encoding="utf-8")
                root = ET.fromstring(xml_text)
                self.assertTrue(root.tag.endswith("svg"))
                self.assertGreater(len(xml_text), 150)

    def test_original_readme_sections_and_catalog_markers_survive(self):
        text_content = (profile.ROOT / "README.md").read_text(encoding="utf-8")
        for i in range(1, 13):
            self.assertIn("## `" + f"{i:02d}" + "`", text_content)
        self.assertIn("PROFILE_REPO_CATALOG_START", text_content)
        self.assertIn("PROFILE_TRACKED_COUNT_START", text_content)
        self.assertIn("three-path-workflow-v3.svg", text_content)
        self.assertIn("The Paisa Journal", text_content)



if __name__ == "__main__":
    unittest.main()
