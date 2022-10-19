$(document).ready(function () {
  // ----- General ----- //
  // General auxiliary variables.
  var currentHost = `${location.protocol}//${location.host}`;
  var csrfToken = $("input[name='csrfmiddlewaretoken']").val();

  // Initialize all tooltips.
  $('[data-toggle="tooltip"]').tooltip();

  // Icons Aux
  $(".fa-trash-o").hover(
    function () {
      $(this).addClass("fa-trash");
      $(this).removeClass("fa-trash-o");
    },
    function () {
      $(this).addClass("fa-trash-o");
      $(this).removeClass("fa-trash");
    }
  );

  // Toasts.
  $(".toast").toast();
  function showToast(message, type) {
    // Clone placeholder and set it up.
    let toast = $(".toast-placeholder").clone();
    toast.removeClass("toast-placeholder");
    toastBody = toast.find(".toast-body");
    toastBody.html(message);

    toast.on("hidden.bs.toast", function () {
      toast.remove();
    });

    switch (type.toLowerCase()) {
      case "success":
        toastBody.addClass("alert-success");
        break;
      case "error":
        toastBody.addClass("alert-danger");
        break;
      case "info":
        toastBody.addClass("alert-info");
        break;
      case "warning":
        toastBody.addClass("alert-warning");
        break;
    }

    // Append and show.
    $("#toastDrawer").append(toast);

    toast.show();
    toast.toast("show");
  }
  // ----- General ----- //

  // ----- Navbar Search ----- //
  var searchVehiclesURL = `${currentHost}/vehicles/search`;
  var vehicleDetailsURL = `${currentHost}/vehicle/`;

  // Bugfix: Use debounce since bootstrap-autocomplete's throttling generated multiple calls.
  var navbarSearchDebounced = _.debounce(function (searchText, callback) {
    $("#navbar-search-icon").css("display", "none");
    $("#navbar-search-loading-spinner").css("display", "inline-block");

    $.ajax({
      url: searchVehiclesURL,
      type: "GET",
      data: {
        q: searchText,
      },
    })
      .done(function (data) {
        callback(data);
      })
      .fail(function (data) {
        alert(
          "An error has occured while searching for the vehicles. Please try again later, or contact the system administrator."
        );
      })
      .always(function (data) {
        $("#navbar-search-loading-spinner").css("display", "none");
        $("#navbar-search-icon").css("display", "inline-block");
      });
  }, 750);

  $(".navbarSearchInput").autoComplete({
    preventEnter: true,
    resolver: "custom",
    events: {
      search: function (searchText, callback) {
        navbarSearchDebounced(searchText, callback);
      },
      searchPost: function (resultsFromServer) {
        // Examples:
        // From server: [{id: 3, identification_number: "654987321", nickname: "Sample vehicle 2"}, {id: 2, identification_number: "987654321", nickname: "Some nickname"}]
        // Expected by bootstrap-autocomplete: [{value: 3, text: "VIN 654987321 - Sample vehicle 2"}, {id: 2, text: "VIN 987654321 - Some nickname"}]
        return _.map(resultsFromServer, function (result) {
          nickname_str = result.nickname ? ` - ${result.nickname}` : "";
          return {
            value: result.identification_number,
            text: `VIN ${result.identification_number}${nickname_str}`,
          };
        });
      },
    },
  });

  $(".navbarSearchInput").on("autocomplete.select", function (e, selectedItem) {
    if (!!selectedItem) {
      window.location = vehicleDetailsURL + selectedItem.value;
    }
  });
  // ----- Navbar Search ----- //

  // ----- Order/Cart Row Add/Remove ----- //
  var upsertCartRowURL = `${currentHost}/orders/cartrow/upsert`;
  var deleteCartRowURL = `${currentHost}/orders/cartrow/delete`;

  var upsertCartRowDebounced = _.debounce(function (
    event,
    vehicleId,
    bomRowId,
    quantity,
    successCallback
  ) {
    $(".loader-container").show();

    $.ajax({
      url: upsertCartRowURL,
      type: "POST",
      data: {
        vehicleId: vehicleId,
        bomRowId: bomRowId,
        quantity: quantity,
        csrfmiddlewaretoken: csrfToken,
      },
    })
      .done(function (data) {
        showToast("Successfully updated cart.", "success");

        if (successCallback) {
          successCallback($(event.target));
        }
      })
      .fail(function (data) {
        showToast(
          "An error has occured while updating the cart. Please try again.",
          "error"
        );
      })
      .always(function (data) {
        $(".loader-container").hide();
      });
  },
  750);

  var deleteCartRowDebounced = _.debounce(function (
    event,
    vehicleId,
    bomRowId,
    successCallback
  ) {
    $(".loader-container").show();

    $.ajax({
      url: deleteCartRowURL,
      type: "POST",
      data: {
        vehicleId: vehicleId,
        bomRowId: bomRowId,
        csrfmiddlewaretoken: csrfToken,
      },
    })
      .done(function (data) {
        showToast("Successfully deleted from cart.", "success");

        if (successCallback) {
          successCallback($(event.target));
        }
      })
      .fail(function (data) {
        showToast(
          "An error has occured while updating the cart. Please try again.",
          "error"
        );
      })
      .always(function (data) {
        $(".loader-container").hide();
      });
  },
  500);

  $(".add-cart-row-btn").on("click", function (e) {
    // Upsert CartRow. Initial Add click.
    let vehicleId = $("#vehicle-id-aux").html();
    let bomRowId = getBOMRowId($(this));
    let quantity = 1; // Initial addition.

    upsertCartRowDebounced(
      e,
      vehicleId,
      bomRowId,
      quantity,
      resetAndInvertRowAddEditVisibility
    );
  });

  $(".upsert-cart-row-input").on("change input keyup", function (e) {
    // If this belongs to a PA, change other members as well (without triggering change event).
    let purchaseAssemblyCode = getPurchaseAssemblyCode($(this));

    if (!!purchaseAssemblyCode) {
      containerSelector = $(
        `.bomrow-container-actions.${purchaseAssemblyCode}`
      );
      changePAUpsertCartRowInputValue(containerSelector, $(this).val());
    }
  });

  $(".upsert-cart-row-input").on("change", function (e) {
    // Upsert CartRow. Subsequent input changes.
    let vehicleId = $("#vehicle-id-aux").html();
    let bomRowId = getBOMRowId($(this));
    let quantity = $(this).val();
    if (quantity == "") {
      $(this).val(0);
    }

    upsertCartRowDebounced(e, vehicleId, bomRowId, quantity);
  });

  $(".delete-cart-row-btn").on("click", function (e) {
    // Upsert CartRow. Delete.
    let vehicleId = $("#vehicle-id-aux").html();
    let bomRowId = getBOMRowId($(this));

    deleteCartRowDebounced(
      e,
      vehicleId,
      bomRowId,
      resetAndInvertRowAddEditVisibility
    );
  });

  function getBOMRowId(currentElement) {
    // Returns current row's BOMRowId.
    return currentElement
      .closest(".bomrow-container-actions")
      .find(".bomrow-id-aux")
      .html();
  }

  function getPurchaseAssemblyCode(currentElement) {
    // Returns current row's PA code, or empty str.
    let rowPurchaseAssembly = currentElement
      .closest(".bomrow-container") // Row Parent
      .find(".purchase-assembly-code");

    let purchaseAssemblyCode = "";
    if (rowPurchaseAssembly.length > 0) {
      purchaseAssemblyCode = rowPurchaseAssembly
        .text()
        .replace(/(\[)|(\])*/g, "");
    }

    return purchaseAssemblyCode;
  }

  function changePAUpsertCartRowInputValue(paContainerSelector, newValue) {
    // Modifies the value of every input related to the PA.
    paContainerSelector.find(".upsert-cart-row-input").val(newValue);
  }

  function invertRowAddEditVisibility(container) {
    // Inverts visibility of row's add or edit actions.
    container
      .find(".add-cart-row-btn, .upsert-cart-row-input, .delete-cart-row-btn")
      .toggle();
  }

  function resetAndInvertRowAddEditVisibility(currentElement) {
    // If this belongs to a PA, change other members as well (without triggering change event).
    let purchaseAssemblyCode = getPurchaseAssemblyCode(currentElement);

    // Display or hide elements. Change values.
    let container = currentElement.closest(".bomrow-container-actions");
    if (!!purchaseAssemblyCode) {
      container = $(`.bomrow-container-actions.${purchaseAssemblyCode}`);
      changePAUpsertCartRowInputValue(container, 1); // Set to 1.
    } else {
      container.find(".upsert-cart-row-input").val(1);
    }

    invertRowAddEditVisibility(container);
  }
  // ----- Order/Cart Row Add/Remove ----- //

  // ----- Shopping Cart ----- //
  $("#shopping-cart-submit-btn").click(function (e) {
    $("#confirmationModal").modal("hide");
    $(".loader-container").show();
  });
  // ----- Shopping Cart ----- //
});
