$(document).ready(function () {
  // ----- BEGIN - AddBOMRow scripts -----
  // Hide forms by default.
  $("#part_or_pa_selection_0").prop("checked", true); // Default value.
  $("#part_or_pa_selection_1").prop("checked", false);
  // $('#part-form').show();  // Default value.
  $("#purchase-assembly-form").hide();
  $("#pa_to_add").val($("#pa_to_add option:first").val()); // Select first option of purchase assembly dropdown.

  // AddBOMRow form radiobutton logic to hide subforms.
  $(document).on("change", "#part_or_pa_selection_0", function () {
    // Show part form.
    if ($(this).is(":checked")) {
      $("#part-form").show();
      $("#purchase-assembly-form").hide();
    }
  });

  $(document).on("change", "#part_or_pa_selection_1", function () {
    // Show purchase assembly form.
    if ($(this).is(":checked")) {
      $("#purchase-assembly-form").show();
      $("#part-form").hide();
    }
  });

  // Get PAs on change and show formsets.
  $("#pa_to_add").on("change", function () {
    // Clean pre-existing formsets.
    $("#locations-formsets").empty();

    if (this.value != -1) {
      // Fetch PA's parts.
      let currentHost = `${location.protocol}//${location.host}`;
      let getPurchaseAssemblyPartsURL = `${currentHost}/admin/parts/purchaseassembly/${this.value}/purchaseassemblypart/getall`;

      // Show loading.
      $(".loader-container").css("display", "block");

      $.ajax({
        url: getPurchaseAssemblyPartsURL,
        type: "GET",
      })
        .done(function (data) {
          // Setup part formsets
          // Update total form count
          $("[name=form-TOTAL_FORMS]").val(data.length);

          // Copy the template and replace prefixes with the correct index
          for (i = 0; i < data.length; i++) {
            // Clone formset template. Note: Must use global replace here
            let $formset_form = $("#locations-formset-template").clone();

            // Set label.
            let pa_part = data[i];
            let part_str = `[${pa_part.part__full_code}] ${pa_part.part__name} (x${pa_part.quantity})`;
            $formset_form
              .find("label")
              .text("Where should part " + part_str + " be placed?");
            $formset_form.find("input[type=hidden]").val(pa_part.id); // Purchase assembly part ID.

            // Get formset HTML and append to form.
            let formset_html = $formset_form
              .html()
              .replace(/__prefix__/g, i)
              .concat("</br><hr></br>");
            $("#locations-formsets").append(formset_html);
          }

          $(".loader-container").css("display", "none");
        })
        .fail(function (data) {
          $(".loader-container").css("display", "none");
          alert(
            "An error has occured while fetching the PA's parts. Please try again, or contact the system administrator."
          );
        });
    }
  });
  // ----- END - AddBOMRow scripts -----
});
