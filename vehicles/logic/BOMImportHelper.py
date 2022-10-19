import os.path
import csv
from io import StringIO

from pprint import pprint
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db.models.functions import Lower
import warnings

warnings.simplefilter(
    action="ignore", category=FutureWarning
)  # Ignore Panda's futurewarnings to avoid development noise.
import pandas as pd

from ..models.VehicleFamily import VehicleFamily
from ..models.Assembly import Assembly
from ..models.Subassembly import Subassembly
from ..models.BOM import BOM
from ..models.BOMRow import BOMRow
from ..exceptions import InvalidImportFileError
from parts.models.Part import Part
from parts.models.PurchaseAssembly import PurchaseAssembly
from parts.models.PurchaseAssemblyPart import PurchaseAssemblyPart
from parts.models.PartSupplier import PartSupplier
from companies.models.Company import Company
from utils.logic.is_integer import is_integer
from utils.logic.save_entity_iterable_to_db import save_entity_iterable_to_db

# TODO: Improve - Review if Panda's automatic type detection could be better than importing every column as str.


class BOMImportHelper:
    """Helper used to validate and process a bill of materials import template."""

    def __init__(self, vehicle_family, user=None):
        if not vehicle_family or not isinstance(vehicle_family, VehicleFamily):
            raise Exception(
                "vehicle_family has to be a VehicleFamily, and cannot be None."
            )
        self.vehicle_family = vehicle_family
        self.user = user
        # Entities to import
        self.assemblies = {}
        self.subassemblies = {}
        self.parts = {}
        self.purchase_assemblies = {}
        self.purchase_assembly_parts = {}
        self.suppliers = {}
        self.supplier_parts = {}
        # Auxiliaries
        self.assembly_codes = set()
        self.subassembly_codes = set()
        self.part_codes = set()
        self.purchase_assembly_codes = set()
        self.supplier_names = set()
        # self.purchase_assembly_part_codes = []
        self.bom_rows = []
        self.errors = []

    # Auxiliary properties
    ROW_PURCHASE_ASSEMBLY_CODE = "purchase_assembly_code"
    ROW_ASSEMBLY_CODE = "assembly_code"
    ROW_ASSEMBLY_NAME = "assembly_name"
    ROW_SUBASSEMBLY_CODE = "subassembly_code"
    ROW_SUBASSEMBLY_NAME = "subassembly_name"
    ROW_PART_CODE = "part_code"
    ROW_PART_SUFFIX = "part_suffix"
    ROW_PART_REVISION = "part_revision"
    ROW_PART_NAME = "part_name"
    ROW_PART_QTY = "part_qty"
    ROW_PART_MATERIAL = "part_material"
    ROW_PART_IS_PURCHASED = "part_is_purchased"
    ROW_PART_NOTES = "part_notes"
    ROW_SUPPLIER_NAME = "supplier_name"
    ROW_PART_DIMENSION_OR_SUPPLIER_CODE = "part_dimensions_or_supplier_code"
    ROW_PURCHASE_COMMENTS = "purchase_comments"
    IMPORT_TEMPLATE_ROWS = (
        ROW_PURCHASE_ASSEMBLY_CODE,
        ROW_ASSEMBLY_CODE,
        ROW_ASSEMBLY_NAME,
        ROW_SUBASSEMBLY_CODE,
        ROW_SUBASSEMBLY_NAME,
        ROW_PART_CODE,
        ROW_PART_SUFFIX,
        ROW_PART_REVISION,
        ROW_PART_NAME,
        ROW_PART_QTY,
        ROW_PART_MATERIAL,
        ROW_PART_IS_PURCHASED,
        ROW_PART_NOTES,
        ROW_SUPPLIER_NAME,
        ROW_PART_DIMENSION_OR_SUPPLIER_CODE,
        ROW_PURCHASE_COMMENTS,
    )
    IMPORT_TEMPLATE_COLUMNS_TO_PROCESS = "A:P"
    IMPORT_TEMPLATE_HEADER_COUNT = 2
    SUPPORTED_FILE_EXTENSIONS = (".csv", ".xlsx", ".xlsm", ".xls")
    DICT_READER_RESTKEY = None
    DICT_READER_RESTVAL = ""

    # Error messages
    ERROR_ROW_MISSING_ENTITY = (
        "Row #{row_number} is missing the required entity: {entity_model_name}."
    )
    ERROR_ROW_MISSING_REQUIRED_ENTITY = "The {entity_model_name} on row #{row_number} is missing the required {required_entity_model_name} on which it depends."
    ERROR_ENTITY_MISSING_FIELDS = "The {entity_model_name} {entity_id} on row #{row_number} is missing required fields."
    ERROR_ENTITY_FULL_CLEAN = "The {entity_model_name} {entity_id} on row #{row_number} has the following error: {error_key} - {error_message}"
    ERROR_ENTITY_DIFFERENT_THAN_EXISTING = "The {entity_model_name} {entity_id} on row #{row_number} has different information than a prior row or the database, on fields: {entity_fields}"
    ERROR_ENTITY_INVALID_VALUE = "The {entity_model_name} {entity_id} on row #{row_number} has an invalid value, on field: {entity_field}"
    ERROR_PURCHASE_ASSEMBLY_INVALID_PARTS = "The Purchase Assembly {entity_id} references different parts in the database, or some of them have errors in the import file which need to be fixed first. DB: {db_parts_contained} / Import: {import_parts_contained}"
    ERROR_ROW_TOTAL_MISMATCH = "The row total in the imported file is different from the correctly detected rows. Please fix other errors."

    # Set error messages auxiliary methods
    def set_error_row_missing_entity(self, row_number, entity_model):
        self.errors.append(
            self.ERROR_ROW_MISSING_ENTITY.format(
                row_number=row_number + self.IMPORT_TEMPLATE_HEADER_COUNT + 1,
                entity_model_name=entity_model.__name__,
            )
        )

    def set_error_row_missing_required_entity(
        self, row_number, entity_model, required_entity_model
    ):
        self.errors.append(
            self.ERROR_ROW_MISSING_REQUIRED_ENTITY.format(
                row_number=row_number + self.IMPORT_TEMPLATE_HEADER_COUNT + 1,
                entity_model_name=entity_model.__name__,
                required_entity_model_name=required_entity_model.__name__,
            )
        )

    def set_error_entity_missing_fields(self, entity_model, entity_id, row_number):
        self.errors.append(
            self.ERROR_ENTITY_MISSING_FIELDS.format(
                entity_model_name=entity_model.__name__,
                entity_id=entity_id,
                row_number=row_number + self.IMPORT_TEMPLATE_HEADER_COUNT + 1,
            )
        )

    def set_error_entity_full_clean(
        self, entity_model, entity_id, row_number, error_key, error_message
    ):
        self.errors.append(
            self.ERROR_ENTITY_FULL_CLEAN.format(
                entity_model_name=entity_model.__name__,
                entity_id=entity_id,
                row_number=row_number + self.IMPORT_TEMPLATE_HEADER_COUNT + 1,
                error_key=error_key,
                error_message=error_message,
            )
        )

    def set_error_entity_different_than_existing(
        self, entity_model, entity_id, row_number, entity_fields
    ):
        self.errors.append(
            self.ERROR_ENTITY_DIFFERENT_THAN_EXISTING.format(
                entity_model_name=entity_model.__name__,
                entity_id=entity_id,
                row_number=row_number + self.IMPORT_TEMPLATE_HEADER_COUNT + 1,
                entity_fields=entity_fields,
            )
        )

    def set_error_entity_invalid_value(
        self, entity_model, entity_id, row_number, entity_field
    ):
        self.errors.append(
            self.ERROR_ENTITY_INVALID_VALUE.format(
                entity_model_name=entity_model.__name__,
                entity_id=entity_id,
                row_number=row_number + self.IMPORT_TEMPLATE_HEADER_COUNT + 1,
                entity_field=entity_field,
            )
        )

    def set_error_purchase_assembly_invalid_parts(
        self, entity_id, db_parts_contained, import_parts_contained
    ):
        self.errors.append(
            self.ERROR_PURCHASE_ASSEMBLY_INVALID_PARTS.format(
                entity_id=entity_id,
                db_parts_contained=db_parts_contained,
                import_parts_contained=import_parts_contained,
            )
        )

    # General auxiliary methods

    def recopilate_entities_identifiers(self, row):
        # Assemblies
        if row[self.ROW_ASSEMBLY_CODE]:
            self.assembly_codes.add(row[self.ROW_ASSEMBLY_CODE])

        # Subassemblies
        if row[self.ROW_ASSEMBLY_CODE] and row[self.ROW_SUBASSEMBLY_CODE]:
            self.subassembly_codes.add(
                row[self.ROW_ASSEMBLY_CODE] + row[self.ROW_SUBASSEMBLY_CODE]
            )

        # Parts
        part_full_code = None
        if row[self.ROW_PART_CODE]:
            part_full_code = self.get_part_full_code_from_row(row)
            self.part_codes.add(part_full_code)

        # PAs
        purchase_assembly_code = None
        if (
            row[self.ROW_PURCHASE_ASSEMBLY_CODE]
            and row[self.ROW_PURCHASE_ASSEMBLY_CODE][0].lower()
            == PurchaseAssembly.PREFIX.lower()
        ):
            purchase_assembly_code = self.get_purchase_assembly_code(row)
            self.purchase_assembly_codes.add(purchase_assembly_code)

        # PAs
        if row[self.ROW_SUPPLIER_NAME]:
            self.supplier_names.add(row[self.ROW_SUPPLIER_NAME].lower())

    def fetch_detected_entities_from_db(self):
        """Fetches the previously identified entities from the database and stores them in memory."""
        db_assemblies = Assembly.objects.filter(
            vehicle_family=self.vehicle_family, code__in=self.assembly_codes
        ).all()
        self.assemblies = {assembly.code: assembly for assembly in db_assemblies}

        db_subassemblies = Subassembly.objects.filter(
            vehicle_family=self.vehicle_family, full_code__in=self.subassembly_codes
        ).all()
        self.subassemblies = {
            subassembly.full_code: subassembly for subassembly in db_subassemblies
        }

        db_parts = (
            Part.objects.filter(full_code__in=self.part_codes)
            .prefetch_related("suppliers")
            .all()
        )
        self.parts = {part.full_code: part for part in db_parts}

        db_purchase_assemblies = PurchaseAssembly.objects.filter(
            code__in=self.purchase_assembly_codes
        ).all()
        self.purchase_assemblies = {pa.full_code: pa for pa in db_purchase_assemblies}

        # db_suppliers = Company.objects.filter(name__in=self.supplier_names).all()
        db_suppliers = (
            Company.objects.annotate(name_lower=Lower("name"))
            .filter(name_lower__in=self.supplier_names)
            .all()
        )
        self.suppliers = {supplier.name.lower(): supplier for supplier in db_suppliers}

    # TODO: Improve - Try to process entities with bulk_create. Review each of the models save method. Separate existing entries. This process does not update.
    def process_bom_entities_to_db(self, bom):
        """Associates received BOM and saves related entities, previously obtained from the import file, to the database."""
        # Associate BOM to rows.
        for row in self.bom_rows:
            row.bom = bom

        # Process each entity dict/list.
        save_entity_iterable_to_db(self.assemblies)
        save_entity_iterable_to_db(self.subassemblies)
        save_entity_iterable_to_db(self.parts)
        save_entity_iterable_to_db(self.suppliers)
        save_entity_iterable_to_db(self.supplier_parts)
        save_entity_iterable_to_db(self.purchase_assemblies)
        save_entity_iterable_to_db(self.purchase_assembly_parts)
        save_entity_iterable_to_db(self.bom_rows)
        self.clear_aux_variables()

    def clear_aux_variables(self):
        """Cleans the auxiliary variables used, such as dictionaries."""
        self.assemblies.clear()
        self.subassemblies.clear()
        self.parts.clear()
        self.purchase_assemblies.clear()
        self.purchase_assembly_parts.clear()
        self.suppliers.clear()
        self.supplier_parts.clear()
        self.assembly_codes.clear()
        self.subassembly_codes.clear()
        self.part_codes.clear()
        self.supplier_names.clear()
        self.purchase_assembly_codes.clear()
        self.bom_rows.clear()
        self.errors.clear()

    def read_import_file_to_dict_list(
        self, import_file_path="", import_file_str="", file_extension=None
    ):
        """Reads the specified file (or str) and returns a list of rows, where each row is a dictionary."""
        if not import_file_path and not import_file_str:
            raise InvalidImportFileError(
                "Invalid import file. Please check that you're correctly uploading the file or contact the system administrator."
            )

        # Get file extension
        if not file_extension and import_file_path:
            filename, file_extension = os.path.splitext(import_file_path)

        if file_extension not in self.SUPPORTED_FILE_EXTENSIONS:
            raise InvalidImportFileError(
                "Invalid import file, supported extensions are: {extensions}".format(
                    extensions=str(self.SUPPORTED_FILE_EXTENSIONS)
                )
            )
        else:
            df = None

            # Read file and obtain Panda DataFrame
            if file_extension == ".csv":
                try:
                    if import_file_str:
                        import_file_str = str(import_file_str, "utf-8")
                    file_to_read = (
                        StringIO(import_file_str)
                        if import_file_str
                        else import_file_path
                    )  # Use str via StringIo if available, else read file.
                    df = pd.read_csv(
                        filepath_or_buffer=file_to_read,
                        dtype=str,
                        skiprows=[0, 1],
                        header=None,
                        names=self.IMPORT_TEMPLATE_ROWS,
                        na_filter=False,
                    )
                except UnicodeDecodeError as e:
                    # Attempt to read file without Panda, using DictReader
                    if import_file_path:
                        with default_storage.open(import_file_path, "r") as csvfile:
                            file_contents = csvfile.read()

                        split_file = file_contents.splitlines()
                        reader = csv.DictReader(
                            f=split_file,
                            fieldnames=self.IMPORT_TEMPLATE_ROWS,
                            restkey=self.DICT_READER_RESTKEY,
                            restval=self.DICT_READER_RESTVAL,
                        )
                        row_list = list(reader)

                        # Skip header lines.
                        for i in range(self.IMPORT_TEMPLATE_HEADER_COUNT):
                            row_list.pop(0)

                        return row_list
                    else:
                        raise UnicodeDecodeError(
                            "Invalid file encoding. Please verify that the file is saved in UTF-8."
                        )

            elif file_extension in (".xlsx", ".xlsm", ".xls"):
                file_to_read = (
                    import_file_str if import_file_str else import_file_path
                )  # Use str if available, else read file.
                df = pd.read_excel(
                    io=file_to_read,
                    dtype=str,
                    skiprows=[0, 1],
                    header=None,
                    names=self.IMPORT_TEMPLATE_ROWS,
                    na_filter=False,
                    index_col=None,
                    usecols=self.IMPORT_TEMPLATE_COLUMNS_TO_PROCESS,  # Hotfix: Panda bug - If file has more columns then it mistakenly takes first column as index.
                )

            # Transform to dictionary
            if df is not None:
                return df.to_dict(orient="records")
            else:
                raise InvalidImportFileError(
                    "Unable to read import file, please contact system administrator."
                )

    def clean_import_row(self, row):
        """Applies cleanup changes to import row, such as removing empty spaces. If row is empty, returns None."""
        is_row_empty = True
        for column, value in row.items():
            if column is not self.DICT_READER_RESTKEY:
                if isinstance(value, str):
                    row[column] = value.strip()
                elif value is None:
                    # If it's None, transform to an empty str to avoid issues later.
                    row[column] = ""

                if is_row_empty and row[column]:
                    is_row_empty = False

        if is_row_empty:
            return None
        else:
            return row

    def try_entity_full_clean(
        self, entity_model, entity, entity_id, row_number, required_entities=()
    ):
        """Tries to execute the entity's full_clean method, and stores returned errors in aux list. Ignores errors due to missing required entities."""
        try:
            entity.full_clean()
        except ValidationError as e:
            for key, value_list in e.message_dict.items():
                # Ignore errors related to required entities, as they'll be added to the DB later and are already checked
                if key not in required_entities:
                    for value in value_list:
                        self.set_error_entity_full_clean(
                            entity_model=entity_model,
                            entity_id=entity_id,
                            row_number=row_number,
                            error_key=key,
                            error_message=value,
                        )

    def compare_entity_rows(
        self, entity_model, entity_1, entity_2, row_number, entity_id
    ):
        """Calls validate_import_comparison in the entity's model and stores returned errors in aux list"""
        comparison_errors = entity_model.validate_import_comparison(entity_1, entity_2)

        if comparison_errors:
            self.set_error_entity_different_than_existing(
                entity_model=entity_model,
                entity_id=entity_id,
                row_number=row_number,
                entity_fields=", ".join(error for error in comparison_errors),
            )

    def try_parse_int_value(
        self, value, entity_model, entity_id, row_number, entity_field
    ):
        """Attempts to parse an int value, or adds an error to the list if unable to."""
        if is_integer(value):
            return True
        else:
            self.set_error_entity_invalid_value(
                entity_model, entity_id, row_number, entity_field
            )
            return False

    def get_part_suffix_from_row(self, row):
        """Gets the correct part suffix from the row, avoiding error when it contains 0."""
        part_suffix_row = row[self.ROW_PART_SUFFIX]
        part_suffix = ""

        # Parse value 0 for suffix to '', as it's a common mistake
        if part_suffix_row and part_suffix_row != "0":
            part_suffix = part_suffix_row

        return part_suffix

    def get_part_full_code_from_row(self, row):
        """Obtains and returns the part's full code from the row, from: code, suffix, revision."""
        part_code = row[self.ROW_PART_CODE]
        part_suffix = self.get_part_suffix_from_row(row)
        part_revision = row[self.ROW_PART_REVISION]
        part_full_code = (
            part_code + part_suffix + part_revision
        )  # Compose code that identifies part uniquely
        return part_full_code

    def fix_part_fields_from_row(self, row, part):
        """Sets the corresponding values to default fields depending on row contents, and returns the part"""
        is_purchased_str = row[self.ROW_PART_IS_PURCHASED]
        if (not is_purchased_str) or (
            is_purchased_str.lower() == "f"
            or is_purchased_str.lower() == Part.IS_FABRICATED_IMPORT_VALUE.lower()
        ):  # Default
            part.is_purchased = False
        elif (
            is_purchased_str.lower() == "t"
            or is_purchased_str.lower() == Part.IS_PURCHASED_IMPORT_VALUE.lower()
        ):
            part.is_purchased = True
        else:
            part.is_purchased = is_purchased_str

        # Apply dimensions only if part is fabricated.
        if not part.is_purchased:
            part.dimension = row[self.ROW_PART_DIMENSION_OR_SUPPLIER_CODE]

        return part

    def get_purchase_assembly_code(self, row):
        """Parses and returns purchase_assembly code, without the A prefix. If code doesn't begin with A, returns empty string."""
        purchase_assembly_code_str = row[self.ROW_PURCHASE_ASSEMBLY_CODE]
        purchase_assembly_code = ""

        if (
            purchase_assembly_code_str
            and purchase_assembly_code_str[0].lower() == PurchaseAssembly.PREFIX.lower()
        ):
            # It's a PA, so we obtain code without A prefix.
            purchase_assembly_code = purchase_assembly_code_str[1:]

        return purchase_assembly_code

    def get_purchase_assembly_part_temp_code(
        self, purchase_assembly_code, part_code, row_number
    ):
        """Obtains a temporary purchase_assembly_part_code, used to identify it during the import process, in order to avoid issues with duplicates in a PA."""
        return "-".join([purchase_assembly_code, part_code, str(row_number)])

    def validate_purchase_assemblies(self):
        """Verifies that the referenced purchase assemblies that already exist in the DB contain the same parts."""
        for (
            purchase_assembly_code,
            purchase_assembly,
        ) in self.purchase_assemblies.items():
            if purchase_assembly.id is not None:
                # Validate parts contained detected in import file vs DB
                detected_purchase_assembly_parts = {
                    k: v
                    for k, v in self.purchase_assembly_parts.items()
                    if purchase_assembly_code in k
                }

                # They must already exist in the DB and be the same
                parts_contained_str = "-".join(
                    sorted(
                        [
                            v.part.full_code
                            for k, v in detected_purchase_assembly_parts.items()
                        ]
                    )
                )
                if purchase_assembly.parts_contained != parts_contained_str:
                    self.set_error_purchase_assembly_invalid_parts(
                        entity_id=purchase_assembly.full_code,
                        db_parts_contained=purchase_assembly.parts_contained,
                        import_parts_contained=parts_contained_str,
                    )

    def validate_row_total(self, row_total):
        """Compares the number of rows read correctly with bom_rows imported."""
        if row_total != len(self.bom_rows):
            # Some errors were found, register error.
            self.errors.append(self.ERROR_ROW_TOTAL_MISMATCH)

    # Parse entities methods
    def parse_assembly(self, row, index):
        """Parses/validates the assembly inside the row and adds it to the BOMImportHelper's list"""

        assembly = Assembly(
            code=row[self.ROW_ASSEMBLY_CODE],
            name=row[self.ROW_ASSEMBLY_NAME],
            vehicle_family=self.vehicle_family,
            created_by=self.user,
            modified_by=self.user,
        )

        if not assembly.code:  # Review empty ID
            self.set_error_row_missing_entity(row_number=index, entity_model=Assembly)
        elif assembly.code in self.assemblies:  # Check if entity has already been added
            # Compare fields, set errors if different
            self.compare_entity_rows(
                entity_model=Assembly,
                entity_1=self.assemblies[assembly.code],
                entity_2=assembly,
                row_number=index,
                entity_id=assembly.code,
            )
        else:
            # First time adding it. Review empty required fields to ensure the user does not reference mistaken entity
            if not assembly.name:
                self.set_error_entity_missing_fields(
                    entity_model=Assembly, entity_id=assembly.code, row_number=index
                )
            else:
                # Validate entity against full_clean method to obtain possible errors, and finally add to aux dict
                self.try_entity_full_clean(
                    entity_model=Assembly,
                    entity=assembly,
                    entity_id=assembly.code,
                    row_number=index,
                )
                self.assemblies[assembly.code] = assembly

    def parse_subassembly(self, row, index):
        """Parses/validates the subassembly inside the row and adds it to the BOMImportHelper's list"""

        subassembly_code = row[self.ROW_SUBASSEMBLY_CODE]
        if not subassembly_code:  # Review empty ID
            return  # Subassembly is optional

        # Review required entities.
        assembly_code = row[self.ROW_ASSEMBLY_CODE]
        if assembly_code and assembly_code in self.assemblies:
            subassembly_full_code = (
                assembly_code + subassembly_code
            )  # Compose code that identifies subassembly uniquely inside an assembly
            subassembly = Subassembly(
                code=subassembly_code,
                name=row[self.ROW_SUBASSEMBLY_NAME],
                vehicle_family=self.vehicle_family,
                assembly=self.assemblies[assembly_code],
                full_code=subassembly_full_code,
                created_by=self.user,
                modified_by=self.user,
            )

            if (
                subassembly_full_code in self.subassemblies
            ):  # Check if entity has already been added
                # Compare fields, set errors if different
                self.compare_entity_rows(
                    entity_model=Subassembly,
                    entity_1=self.subassemblies[subassembly_full_code],
                    entity_2=subassembly,
                    row_number=index,
                    entity_id=subassembly.code,
                )
            else:
                # First time adding it. Review empty required fields to ensure the user does not reference mistaken entity
                if not subassembly.name:
                    self.set_error_entity_missing_fields(
                        entity_model=Subassembly,
                        entity_id=subassembly.code,
                        row_number=index,
                    )
                else:
                    # Validate entity against full_clean method to obtain possible errors, and finally add to aux dict
                    required_entities = ("assembly", "vehicle_family")
                    self.try_entity_full_clean(
                        entity_model=Subassembly,
                        entity=subassembly,
                        entity_id=subassembly.code,
                        row_number=index,
                        required_entities=required_entities,
                    )
                    self.subassemblies[subassembly_full_code] = subassembly

    def parse_part(self, row, index):
        """Parses/validates the part inside the row and adds it to the BOMImportHelper's list"""

        part_code = row[self.ROW_PART_CODE]
        part_suffix = self.get_part_suffix_from_row(row)
        part_revision = row[self.ROW_PART_REVISION]
        part_full_code = (
            part_code + part_suffix + part_revision
        )  # Compose code that identifies part uniquely

        if not part_code:  # Review empty ID
            self.set_error_row_missing_entity(row_number=index, entity_model=Part)
        else:
            # Review if part code/suffix is int
            if self.try_parse_int_value(
                value=part_code,
                entity_model=Part,
                entity_id=part_full_code,
                row_number=index,
                entity_field="code",
            ) and (
                part_suffix == ""
                or self.try_parse_int_value(
                    value=part_suffix,
                    entity_model=Part,
                    entity_id=part_full_code,
                    row_number=index,
                    entity_field="suffix",
                )
            ):
                # Review required entities.
                assembly_code = row[self.ROW_ASSEMBLY_CODE]
                subassembly_code = row[self.ROW_SUBASSEMBLY_CODE]
                subassembly_full_code = assembly_code + subassembly_code
                if (assembly_code and assembly_code in self.assemblies) and (
                    (not subassembly_code)
                    or (
                        subassembly_code and subassembly_full_code in self.subassemblies
                    )
                ):
                    part = Part(
                        code=part_code,
                        suffix=None if part_suffix == "" else part_suffix,
                        revision=part_revision,
                        name=row[self.ROW_PART_NAME],
                        material=row[self.ROW_PART_MATERIAL],
                        notes=row[self.ROW_PART_NOTES],
                        full_code=part_full_code,
                        created_by=self.user,
                        modified_by=self.user,
                    )
                    part = self.fix_part_fields_from_row(row, part)
                    if (
                        part_full_code in self.parts
                    ):  # Check if entity has already been added
                        # Compare fields, set errors if different
                        self.compare_entity_rows(
                            entity_model=Part,
                            entity_1=self.parts[part_full_code],
                            entity_2=part,
                            row_number=index,
                            entity_id=part_full_code,
                        )
                    else:
                        # First time adding it. Review empty required fields to ensure the user does not reference mistaken entity
                        if not part.name:
                            self.set_error_entity_missing_fields(
                                entity_model=Part,
                                entity_id=part_full_code,
                                row_number=index,
                            )
                        else:
                            # Validate entity against full_clean method to obtain possible errors, and finally add to aux dict
                            self.try_entity_full_clean(
                                entity_model=Part,
                                entity=part,
                                entity_id=part_full_code,
                                row_number=index,
                            )
                            self.parts[part_full_code] = part

    def parse_purchase_assembly(self, row, index):
        """Parses/validates the purchase assembly inside the row and adds it to the BOMImportHelper's list"""
        purchase_assembly_code = self.get_purchase_assembly_code(row)
        purchase_assembly_full_code = row[self.ROW_PURCHASE_ASSEMBLY_CODE]

        # Check if PA code has contents and is an integer
        if purchase_assembly_code and self.try_parse_int_value(
            value=purchase_assembly_code,
            entity_model=PurchaseAssembly,
            entity_id=purchase_assembly_full_code,
            row_number=index,
            entity_field="code",
        ):
            # Check if part exists
            part_full_code = self.get_part_full_code_from_row(row)
            if part_full_code and part_full_code in self.parts:
                # Check if PA has not been created
                if purchase_assembly_full_code not in self.purchase_assemblies:
                    # Create PA
                    purchase_assembly = PurchaseAssembly(
                        code=purchase_assembly_code,
                        full_code=purchase_assembly_full_code,
                        created_by=self.user,
                        modified_by=self.user,
                    )
                    self.try_entity_full_clean(
                        entity_model=PurchaseAssembly,
                        entity=purchase_assembly,
                        entity_id=purchase_assembly_full_code,
                        row_number=index,
                    )
                    self.purchase_assemblies[
                        purchase_assembly_full_code
                    ] = purchase_assembly

    def parse_purchase_assembly_part(self, row, index):
        """Parses/validates the purchase assembly part inside the row and adds it to the BOMImportHelper's list"""
        purchase_assembly_full_code = row[self.ROW_PURCHASE_ASSEMBLY_CODE]
        part_full_code = self.get_part_full_code_from_row(row)

        if (
            purchase_assembly_full_code
            and purchase_assembly_full_code in self.purchase_assemblies
            and part_full_code
            and part_full_code in self.parts
        ):
            purchase_assembly_part_temp_code = (
                self.get_purchase_assembly_part_temp_code(
                    purchase_assembly_code=self.purchase_assemblies[
                        purchase_assembly_full_code
                    ].full_code,
                    part_code=part_full_code,
                    row_number=index + 1,
                )
            )

            # Review if qty is a correct integer
            quantity = row[self.ROW_PART_QTY]
            quantity = (
                1 if not quantity or quantity == "0" else quantity
            )  # Part quantity default value
            if self.try_parse_int_value(
                value=quantity,
                entity_model=Part,
                entity_id=part_full_code,
                row_number=index,
                entity_field="quantity",
            ):
                # Create PAvsPart
                purchase_assembly = self.purchase_assemblies[
                    purchase_assembly_full_code
                ]
                part = self.parts[part_full_code]
                quantity = int(quantity)
                purchase_assembly_part = PurchaseAssemblyPart(
                    purchase_assembly=purchase_assembly,
                    part=part,
                    quantity=quantity,
                    full_code=purchase_assembly_part_temp_code,
                )
                # Look for entity in DB
                # Edge case - Avoid fetching the same repeated PA parts, just in case a PA part with the same part and quantity exists in a PA.
                pa_part_ids = [
                    pa_part.pk
                    for pa_part_str, pa_part in self.purchase_assembly_parts.items()
                    if pa_part.pk
                ]
                db_entity = (
                    PurchaseAssemblyPart.objects.filter(
                        purchase_assembly=purchase_assembly,
                        part=part,
                        quantity=quantity,
                    )
                    .exclude(pk__in=pa_part_ids)
                    .first()
                )
                if db_entity is None:
                    required_entities = ("purchase_assembly", "part")
                    self.try_entity_full_clean(
                        entity_model=PurchaseAssemblyPart,
                        entity=purchase_assembly_part,
                        entity_id=purchase_assembly_part_temp_code,
                        row_number=index,
                        required_entities=required_entities,
                    )
                    self.purchase_assembly_parts[
                        purchase_assembly_part_temp_code
                    ] = purchase_assembly_part
                else:
                    self.purchase_assembly_parts[
                        purchase_assembly_part_temp_code
                    ] = db_entity
                    self.compare_entity_rows(
                        entity_model=PurchaseAssemblyPart,
                        entity_1=self.purchase_assembly_parts[
                            purchase_assembly_part_temp_code
                        ],
                        entity_2=purchase_assembly_part,
                        row_number=index,
                        entity_id=purchase_assembly_part_temp_code,
                    )

    def parse_part_supplier(self, row, index):
        """Parses/validates the part's supplier inside the row and adds it to the BOMImportHelper's list"""
        supplier_name = row[self.ROW_SUPPLIER_NAME]

        # Check that row has supplier name
        if supplier_name:
            # Check if part exists
            supplier_name_lower = supplier_name.lower()
            part_full_code = self.get_part_full_code_from_row(row)
            if part_full_code and part_full_code in self.parts:
                if supplier_name_lower in self.suppliers:
                    if self.suppliers[supplier_name_lower].is_supplier is False:
                        self.suppliers[supplier_name_lower].is_supplier = True
                else:
                    # Create supplier
                    supplier = Company(
                        name=supplier_name,
                        is_supplier=True,
                        is_customer=False,
                        created_by=self.user,
                        modified_by=self.user,
                    )
                    self.try_entity_full_clean(
                        entity_model=Company,
                        entity=supplier,
                        entity_id=supplier_name,
                        row_number=index,
                    )
                    self.suppliers[supplier_name_lower] = supplier

                # Review supplier part.
                part_supplier_temp_code = f"{supplier_name_lower} - {part_full_code}"
                supplier_part_number = (
                    row[self.ROW_PART_DIMENSION_OR_SUPPLIER_CODE]
                    if self.parts[part_full_code].is_purchased
                    else ""
                )  # Row contains this information only if it's purchased.
                part_supplier = PartSupplier(
                    part=self.parts[part_full_code],
                    company=self.suppliers[supplier_name_lower],
                    supplier_part_number=supplier_part_number,
                    purchase_comments=row[self.ROW_PURCHASE_COMMENTS],
                    created_by=self.user,
                    modified_by=self.user,
                )
                if part_supplier_temp_code in self.supplier_parts:
                    # Compare fields, set errors if different
                    self.compare_entity_rows(
                        entity_model=PartSupplier,
                        entity_1=self.supplier_parts[part_supplier_temp_code],
                        entity_2=part_supplier,
                        row_number=index,
                        entity_id=part_supplier_temp_code,
                    )
                else:
                    # Validate entity against full_clean method to obtain possible errors, and finally add to aux dict
                    required_entities = ("part", "company")
                    self.try_entity_full_clean(
                        entity_model=PartSupplier,
                        entity=part_supplier,
                        entity_id=part_supplier_temp_code,
                        row_number=index,
                        required_entities=required_entities,
                    )
                    self.supplier_parts[part_supplier_temp_code] = part_supplier

    def unify_bom_row(self, row, index):
        """Unifies the BOMRow formed by the entities added to the BOMImportHelper during the import process, using the import row."""
        # Review required entities.
        assembly_code = row[self.ROW_ASSEMBLY_CODE]

        if assembly_code and assembly_code in self.assemblies:
            purchase_assembly_full_code = row[self.ROW_PURCHASE_ASSEMBLY_CODE]
            part_full_code = self.get_part_full_code_from_row(row)
            assembly = self.assemblies[assembly_code]
            subassembly = None  # Subassembly is optional.

            subassembly_full_code = (
                assembly_code + row[self.ROW_SUBASSEMBLY_CODE]
            )  # Compose code that identifies subassembly uniquely inside an assembly
            if subassembly_full_code and subassembly_full_code in self.subassemblies:
                subassembly = self.subassemblies[subassembly_full_code]

            if (
                purchase_assembly_full_code
                and (
                    purchase_assembly_full_code[0].lower()
                    == PurchaseAssembly.PREFIX.lower()
                )
                and purchase_assembly_full_code in self.purchase_assemblies
            ):
                # It's a PA member.
                purchase_assembly_part_temp_code = (
                    self.get_purchase_assembly_part_temp_code(
                        purchase_assembly_code=self.purchase_assemblies[
                            purchase_assembly_full_code
                        ].full_code,
                        part_code=part_full_code,
                        row_number=index + 1,
                    )
                )
                if (
                    purchase_assembly_part_temp_code
                    and purchase_assembly_part_temp_code in self.purchase_assembly_parts
                ):
                    purchase_assembly_part = self.purchase_assembly_parts[
                        purchase_assembly_part_temp_code
                    ]

                    # Add BOMRow
                    bom_row = BOMRow(
                        bom=None,  # BOM will be added later, when processing the rows against the DB.
                        assembly=assembly,
                        subassembly=subassembly,
                        part=None,  # It's a PA, so part must be None.
                        purchase_assembly_part=purchase_assembly_part,
                        quantity=1,  # It's a PA, so quantity must be 1 (for now), since part quantity is in the purchase_assembly_part.
                        created_by=self.user,
                        modified_by=self.user,
                    )
                    self.bom_rows.append(bom_row)
            elif part_full_code and part_full_code in self.parts:
                # It's an individual part.
                part = self.parts[part_full_code]

                # Parse part quantity
                quantity = row[self.ROW_PART_QTY]
                quantity = (
                    1 if not quantity or quantity == "0" else quantity
                )  # Part quantity default value
                if self.try_parse_int_value(
                    value=quantity,
                    entity_model=Part,
                    entity_id=part_full_code,
                    row_number=index,
                    entity_field="quantity",
                ):
                    # Add BOMRow
                    bom_row = BOMRow(
                        bom=None,  # BOM will be added later, when processing the rows against the DB.
                        assembly=assembly,
                        subassembly=subassembly,
                        part=part,
                        purchase_assembly_part=None,  # It's a part, so PA must be None.
                        quantity=quantity,
                        created_by=self.user,
                        modified_by=self.user,
                    )
                    self.bom_rows.append(bom_row)

    def parse_import_rows(self, file_contents_dict, print_output=False):
        """Splits the file contents into rows, and then validates and parses the different related entities into auxiliary dictionaries."""
        # Fetch needed entities and store them.
        for index, row in enumerate(file_contents_dict):
            # Cleanup row, and skip empty ones
            row = self.clean_import_row(row=row)
            if row is not None:
                self.recopilate_entities_identifiers(row)
        self.fetch_detected_entities_from_db()

        # Parse rows into entities.
        row_total = 0
        for index, row in enumerate(file_contents_dict):
            # Cleanup row, and skip empty ones
            row = self.clean_import_row(row=row)
            if row is not None:
                self.parse_assembly(row=row, index=index)
                self.parse_subassembly(row=row, index=index)
                self.parse_part(row=row, index=index)
                self.parse_part_supplier(row=row, index=index)
                self.parse_purchase_assembly(row=row, index=index)
                self.parse_purchase_assembly_part(row=row, index=index)
                self.unify_bom_row(row=row, index=index)
                row_total += 1

        self.validate_purchase_assemblies()
        self.validate_row_total(row_total=row_total)

        # TODO: Log everything depending on environment setting.
        if print_output:
            print("----- ASSEMBLIES -----")
            pprint(self.assemblies)
            print("----- SUBASSEMBLIES -----")
            pprint(self.subassemblies)
            print("----- PARTS -----")
            pprint(self.parts)
            print("----- PURCHASE_ASSEMBLIES -----")
            pprint(self.purchase_assemblies)
            print("----- PURCHASE_ASSEMBLY_PARTS -----")
            pprint(self.purchase_assembly_parts)
            print("----- BOM_ROWS -----")
            pprint(self.bom_rows)
            print("----- SUPPLIERS -----")
            pprint(self.suppliers)
            print("----- SUPPLIER PARTS -----")
            pprint(self.supplier_parts)
            print("----- ERRORS -----")
            print("\n\n".join(self.errors))
