import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "product_references", Path(__file__).resolve().parent.parent / "scripts/check-product-references.py"
)
refs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refs)


class ProductReferences(unittest.TestCase):
    def test_installed_hosted_widget_is_allowed(self):
        refs.check_reference(refs.APP_BLOCK, "blocks")

    def test_unknown_hosted_widget_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            refs.check_reference("shopify://apps/unknown/blocks/widget/id", "blocks")

    def test_missing_local_block_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            refs.check_reference("nonexistent-product-reference", "blocks")


if __name__ == "__main__":
    unittest.main()
