import os
import logging

from django import forms
from django.core.validators import ValidationError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from ..exceptions import InvalidImportFileError
from ..logic.BOMImportHelper import BOMImportHelper
from ..models.BOM import BOM


class BOMAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.import_helper = None

        # Hide import_file during saveasnew, since it's not required.
        if self.is_saveasnew:
            self.fields["import_file"].widget = self.fields[
                "import_file"
            ].hidden_widget()

    class Meta:
        model = BOM
        fields = [
            "vehicle_family",
            "name",
            "code",
            "description",
            "revision",
            "revision_notes",
            "import_file",
            "thumbnail",
            "files",
        ]

    def clean(self):
        cleaned_data = super(BOMAdminForm, self).clean()
        error_list = []

        # Parse and validate imported file, only on create.
        if self.instance.id is None:
            vehicle_family = cleaned_data.get("vehicle_family")
            import_file = cleaned_data.get("import_file")

            if not self.is_saveasnew:  # Only on new creation from scratch.
                if not vehicle_family:
                    self.add_error(
                        "vehicle_family",
                        "The vehicle family is required when first adding the BOM.",
                    )

                if not import_file:
                    self.add_error(
                        "import_file",
                        "The import file is required when first adding the BOM.",
                    )

                if vehicle_family and import_file:
                    filename, file_extension = os.path.splitext(import_file.name)
                    try:
                        import_file_str = import_file.read()

                        # Hotfix: CSV - Temporarily save file to have a fallback in case reading bytes fails.
                        temp_import_file_path = ""
                        if file_extension == ".csv":
                            temp_import_file_path = default_storage.save(
                                "tmp/" + import_file.name, ContentFile(import_file_str)
                            )

                        self.import_helper = BOMImportHelper(
                            vehicle_family=vehicle_family, user=self.user
                        )
                        row_dict_list = (
                            self.import_helper.read_import_file_to_dict_list(
                                import_file_path=temp_import_file_path,
                                import_file_str=import_file_str,
                                file_extension=file_extension,
                            )
                        )
                        self.import_helper.parse_import_rows(row_dict_list)
                    except InvalidImportFileError as e:
                        raise ValidationError(e.message)
                    except Exception as e:
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error: {e}")
                        raise ValidationError(
                            "There was an error processing your import file, please refer to the documentation or contact the system administrator for support."
                        )
                    finally:
                        # Delete temp file, if created.
                        if (
                            file_extension
                            and file_extension == ".csv"
                            and default_storage.exists(temp_import_file_path)
                        ):
                            default_storage.delete(temp_import_file_path)

                    if self.import_helper.errors:
                        for index, error in enumerate(self.import_helper.errors, 1):
                            error_list.append(
                                ValidationError(
                                    error, code="import_error " + str(index)
                                )
                            )
                        raise ValidationError(error_list)
