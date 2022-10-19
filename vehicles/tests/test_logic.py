from pathlib import Path

from django.test import TestCase, Client
from django.urls import reverse
from pandas import read_excel

# Paths must be app based, not relative for tests.
from vehicles.models.VehicleFamily import VehicleFamily
from vehicles.models.BOM import BOM
from vehicles.logic.BOMImportHelper import BOMImportHelper

# BOM Import tests
class ImportLogicTestCase(TestCase):
    full_excel_import_file_path = (
        Path(__file__).parent / "auxiliary/BOM_Import_Template_v2_QA.xlsx"
    )

    full_csv_import_file_path = (
        Path(__file__).parent / "auxiliary/BOM_Import_Template_v2_QA.csv"
    )

    incomplete_csv_import_file_with_errors_path = (
        Path(__file__).parent / "auxiliary/BOM_Import_Template_v2_QA_Errors.csv"
    )

    # Load prior existing data for test purposes
    fixtures = ["vehicles_sample_existing_data.json"]

    def post_bom_import(self, path):
        """Performs an E2E test that executes a BOM import process against the admin."""
        # Log in user.
        c = Client()
        c.login(username="sxadmin", password="sx.4321")
        add_url = reverse("admin:vehicles_bom_add")

        # Prepare form data.
        vehicle_family = VehicleFamily.objects.first()
        with open(path, "rb") as import_file:
            data = {
                "vehicle_family": vehicle_family.id,
                "name": "Mosaic Tractor X",
                "code": "MTX",
                "import_file": import_file,
            }

            # Post form and return response.
            return c.post(add_url, data)

    def test_bom_admin_correct_import(self):
        """E2E test that validates that a correct import file generates the BOM in the DB."""
        # Post BOM import form.
        response = self.post_bom_import(self.full_excel_import_file_path)
        self.assertEqual(response.status_code, 302)  # Redirects to BOM admin

        # Assert BOM was added
        latest_bom = BOM.objects.last()
        self.assertEqual(latest_bom.code, "MTX")

    def test_import_incorrect_file_csv(self):
        """Validates separating the file's contents into BOMImportRows from an incorrect file"""
        # Post BOM import form.
        response = self.post_bom_import(
            self.incomplete_csv_import_file_with_errors_path
        )

        # Assert errors were generated
        self.assertNotEqual(response.status_code, 302)

    def test_read_full_csv_file(self):
        """Validates that the csv file's contents can be read correctly into a list of dictionaries."""
        # Post BOM import form. No exception should be raised.
        response = self.post_bom_import(self.full_csv_import_file_path)
