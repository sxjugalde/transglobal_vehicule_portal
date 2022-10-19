from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

# Paths must be app based, not relative for tests.
from parts.models.Part import Part
from parts.models.PurchaseAssembly import PurchaseAssembly
from parts.models.PurchaseAssemblyPart import PurchaseAssemblyPart


# Part
class PartModelTests(TestCase):
    def test_str(self):
        """Validates part's __str__"""
        new_part = Part(code=12345, name="Sample part 1", suffix=1, revision="A")
        new_part.save()
        saved_part = Part.objects.last()
        self.assertEqual(str(saved_part), "123451A - Sample part 1")

    def test_get_default_part_code(self):
        """Ensures the default part code is obtained correctly."""
        code = Part.get_next_part_code()
        self.assertEqual(code, 20001)

    def test_get_next_part_code(self):
        """Ensures the next available part code is obtained correctly."""
        new_part = Part(code=20999, name="Sample part 1")
        new_part.save()
        code = Part.get_next_part_code()
        self.assertEqual(code, 21000)

    def test_verify_valid_part_code(self):
        """Verifies part full code validations."""
        # Code has to be 5 digits long
        new_part = Part(code=123456, name="Sample part 1")
        with self.assertRaises(ValidationError, msg="Code has to be 5 digits long."):
            new_part.full_clean()

        new_part.code = 1234
        with self.assertRaises(ValidationError, msg="Code has to be 5 digits long."):
            new_part.full_clean()

        # Suffix has to be greater than 0.
        new_part.code = 12345
        new_part.suffix = 0
        with self.assertRaises(ValidationError):
            new_part.full_clean()

        # Revision has to be 1 letter long.
        new_part.suffix = 1
        new_part.revision = "AB"
        with self.assertRaises(ValidationError):
            new_part.full_clean()

    def test_get_full_code(self):
        """Validates that the part's full code is returned correctly after save."""
        new_part = Part(code=12345, name="Sample part 1")
        new_part.save()
        saved_part = Part.objects.last()
        self.assertEqual(saved_part.full_code, "12345")

        saved_part.suffix = 1
        saved_part.revision = "A"
        saved_part.save()
        self.assertEqual(saved_part.full_code, "123451A")

    def test_unique_code(self):
        """Validates only one code can be inserted, composed by code, suffix and revision."""
        new_part = Part(code=12345, name="Sample part 1", suffix=1, revision="A")
        new_part.save()
        new_part_2 = Part(code=12345, name="Sample part 2", suffix=1, revision="A")
        with self.assertRaises(IntegrityError):
            new_part_2.save()


# Purchase Assembly
class PurchaseAssemblyModelTests(TestCase):
    def test_str(self):
        """Validates PA's __str__"""
        new_pa = PurchaseAssembly(code=1234567)
        new_pa.save()
        saved_pa = PurchaseAssembly.objects.last()
        self.assertEqual(str(saved_pa), "A1234567")

    def test_get_default_pa_code(self):
        """Ensures the default PA code is obtained correctly."""
        code = PurchaseAssembly.get_next_purchase_assembly_code()
        self.assertEqual(code, 1000201)

    def test_get_next_pa_code(self):
        """Ensures the next available PA code is obtained correctly."""
        new_pa = PurchaseAssembly(code=1999999)
        new_pa.save()
        code = PurchaseAssembly.get_next_purchase_assembly_code()
        self.assertEqual(code, 2000000)

    def test_verify_valid_pa_code(self):
        """Verifies PA code validations."""
        # Code has to be 7 digits long
        new_pa = PurchaseAssembly(code=123456)
        with self.assertRaises(ValidationError, msg="Code has to be 7 digits long."):
            new_pa.full_clean()

        new_pa.code = 12345678
        with self.assertRaises(ValidationError, msg="Code has to be 7 digits long."):
            new_pa.full_clean()

    def test_parts_contained(self):
        """Validates parts_contained auxiliary str generation."""
        # Parts
        new_part = Part(code=12345, name="Sample part 1", suffix=1, revision="A")
        new_part_2 = Part(code=12345, name="Sample part 1", suffix=2, revision="A")
        new_part.save()
        new_part_2.save()
        # PA
        new_pa = PurchaseAssembly.objects.create(code=1234567)
        new_pa.parts.set([new_part, new_part_2])
        new_pa.update_parts_contained()
        saved_pa = PurchaseAssembly.objects.last()
        self.assertEqual(saved_pa.parts_contained, "123451A-123452A")
