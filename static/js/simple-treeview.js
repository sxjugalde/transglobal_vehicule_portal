$(document).ready(function () {
  // ----- Treeview toggle ----- //
  var toggler = document.getElementsByClassName("caret");
  var i;

  for (i = 0; i < toggler.length; i++) {
    toggler[i].addEventListener("click", function () {
      this.closest(".treeview-branch")
        .querySelector(".nested")
        .classList.toggle("active");
      this.classList.toggle("caret-down");
    });
  }
  // ----- Treeview toggle ----- //

  // ----- Treeview filter ----- //
  $("#treeview-filter").keyup(function () {
    let searchTextLower = $(this).val().toLowerCase();
    // let searchTextLower = $(this).val().toLowerCase();

    // Hotfix: If searching for a PA, avoid filtering it's children.
    let purchaseAssemblyPattern = new RegExp("^([a]{1})(\\d*)$");
    let isFilteringPurchaseAssembly = purchaseAssemblyPattern.test(
      searchTextLower
    );

    $("#simple-treeview")
      .find("ul > li")
      .each(function () {
        let currentLiTextLower = $(this).text().toLowerCase();
        let textToCheck = currentLiTextLower;

        // Check if li is a member of a PA.
        if (isFilteringPurchaseAssembly) {
          // Use PA li as search aux to avoid filtering it's members.
          let purchaseAssemblyLi = $(this).hasClass(".purchase-assembly")
            ? $(this)
            : $(this).closest(".purchase-assembly");

          if (purchaseAssemblyLi.length) {
            textToCheck = purchaseAssemblyLi.text().toLowerCase();
          }
        }

        // Filter li which contain search text
        let showCurrentLi = textToCheck.indexOf(searchTextLower) !== -1;

        $(this).toggle(showCurrentLi);
      });
  });

  $(".part-code").click(function () {
    let contents = $(this)
      .text()
      .replace(/(\[)|(\])*/g, "");

    $("#treeview-filter").val(contents).trigger("keyup");
  });

  $(".purchase-assembly-filter").click(function () {
    let contents = $(this)
      .closest(".bomrow-container")
      .find(".purchase-assembly-code")
      .text()
      .replace(/(\[)|(\])*/g, "");

    $("#treeview-filter").val(contents).trigger("keyup");
  });
  // ----- Treeview filter ----- //
});
