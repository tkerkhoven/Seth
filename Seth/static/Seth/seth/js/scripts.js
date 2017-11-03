var oldto = 5.5;
var oldfrom = 5;
var searchString = "";
var highlighted = "";

$(".btn").mouseup(function(){
    $(this).blur();
});

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function BlurEdit() {
    var text = $(this).val();
    var viewableText = $("<a></a>");
    if(text == "" || parseInt(text) < $(this).attr("min") || parseInt(text) > $(this).attr("max")) {
        viewableText.html($(this).attr('old'));
        viewableText.attr('id', $(this).attr('id'));
        viewableText.attr('title', $(this).attr('title'));
        $("#remove_grade_a").remove();
        highlighted = "";
        $(this).replaceWith(viewableText);
    }
    else {
        oldHtml = $(this).attr("old");

        viewableText.html($(this).attr('old'));
        viewableText.attr('id', $(this).attr('id'));
        viewableText.attr('title', $(this).attr('title'));
        $("#remove_grade_a").remove();
        highlighted = "";
        $(this).replaceWith(viewableText);

        if(text != oldHtml) {
            $("#modal_yes").attr("data-url", $(this).attr("data-url"));
            $("#modal_yes").attr("v-text", viewableText.attr("id"));
            $("#modal_yes").attr("text", text);
            $("#modal_yes").attr("func", "edit");
            $("#modal-p").html("Are you sure you want to change " + viewableText.parent().siblings(".s_class").first().find("a").first().html() + "'s grade from " + oldHtml + " to " + text + "?");
            $("#gradeModal").modal("show");
        }
    }
};

var gradeApp = angular.module("gradeApp", []);

gradeApp.controller('studentController', function($scope,$http) {
    url = $("#gradeboo2k").attr("data-url")

    $.ajax({
        url: url,
        method: "GET",
        dataType: "json",
        success: function(data) {
            console.log(data)
            $scope.students = data
        }
    });
});

$(document).ready(function() {

    var table = $('#gradebook').on( 'processing.dt', function ( e, settings, processing ) {
        $('#processingIndicator').css( 'display', processing ? 'block' : 'none');
      } ).DataTable({
      "ordering": false,
      "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
      "scrollX": true,

      "processing": true,
      "language": { 'processing': '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i><span class="sr-only">Loading...</span>',
                    'emptyTable': '<a class="float-left">No grades found!</a>'},

      "ajax": {
        "url": $("#gradebook").attr("data-url"),
        "method": "GET",
        "data": {
          "view": $("#gradebook").attr("data-view"),
        },
      },

      createdRow: function( row, data, dataIndex ) {
        // Set the data-status attribute, and add a class
        $(row).find('td:eq(0)').addClass('s_class nowrap');

        $(row).children(":not(.s_class)").each(function() {
          a = $(this).find("a");
          $(this).attr("id", "gradeid_" + a.attr("id").split("_")[1] + "_" + a.attr("id").split("_")[2]);
        });
      },

      drawCallback: function(settings){
        var api = this.api();

        $('td', api.table().container()).tooltip({
           container: 'body'
        });
      }
    });

    var assign_table = $('#assignment_table').on( 'processing.dt', function ( e, settings, processing ) {
        $('#processingIndicator').css( 'display', processing ? 'block' : 'none');
      } ).DataTable({
      "ordering": false,
      "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
      "scrollX": true,

      "processing": true,
      "language": { 'processing': '<i class="fa fa-spinner fa-pulse fa-3x fa-fw"></i><span class="sr-only">Loading...</span>',
                    'emptyTable': '<a class="float-left">No grades found!</a>'},

      "ajax": {
        "url": $("#assignment_table").attr("data-url"),
        "method": "GET",
        "data": {
          "view": $("#gradebook").attr("data-view"),
        },
      },

      createdRow: function( row, data, dataIndex ) {
        // Set the data-status attribute, and add a class
        $(row).find('td:eq(0)').addClass('s_class nowrap');

        $(row).children(":not(.s_class)").each(function() {
          a = $(this).find("a");
          $(this).attr("id", "gradeid_" + a.attr("id").split("_")[1] + "_" + a.attr("id").split("_")[2]);
        });
      },

      drawCallback: function(settings){
        var api = this.api();

        $('td', api.table().container()).tooltip({
           container: 'body'
        });
      }
    });

    table.on('draw', function() {
      $('[data-toggle="popover"]').popover();
      updateColoring();
    });

    assign_table.on('draw', function() {
      $('[data-toggle="popover"]').popover();
      updateColoring();
    });

    $('a[data-toggle="tab"]').on( 'shown.bs.tab', function (e) {
        $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
        $($(e.relatedTarget).attr("href")).attr("class", "tab-pane fade")
    });

    $('[id^="collapsePart"').on('show.bs.collapse', function () {
      var id = $(this).attr("data-id");
      $("#mp_collapse" + id).find("i").html("arrow_drop_up");
    })
    $('[id^="collapsePart"').on('hide.bs.collapse', function () {
      var id = $(this).attr("data-id");
      $("#mp_collapse" + id).find("i").html("arrow_drop_down");
    })

    $("#modal_yes").on("mousedown", function() {

      if($("#modal_yes").attr("func") == "remove") {
          var url = $("#modal_yes").attr('data-url');
          var changeID = $("#modal_yes").attr('data-id');
          var change = $("#" + changeID).find("a");

          var oldHtml = change.html();
          change.html('<i class="material-icons">loop</i>');
          change.parent().removeClass("success warning error loading");
          change.parent().addClass("loading");

          $.ajax({
            url:url,

            method: "GET",
            dataType: "json",

            success: function(data) {
              if(data.deleted) {
                change.attr("title", "N/A");
                change.html("-");
                change.attr("data-grade", "-");
                updateOrRemoveColoring(change.parent());
              }
              else {
                change.html(oldHtml);
                updateOrRemoveColoring(change.parent());
              }
            },

            error: function(data) {
              change.html(oldHtml);
              updateOrRemoveColoring(change.parent());
            }
          });
      }
      else if($("#modal_yes").attr("func") == "edit") {
        viewableText = $("#" + $("#modal_yes").attr("v-text"));
        text = $("#modal_yes").attr("text");

        viewableText.html('<i class="material-icons">loop</i>');
        viewableText.attr('data-url', $("#modal_yes").attr('data-url'));

        viewableText.parent().removeClass("success warning error loading");
        viewableText.parent().addClass("loading");

        var csrftoken = getCookie('csrftoken');
        $.ajax({
          beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
          },

          url: $(this).attr('data-url'),
          data: {
            'grade': parseFloat(text)
          },

          method: "POST",
          dataType: 'json',

          success: function(data) {
            viewableText.attr("data-grade", data.grade);
            viewableText.html(data.grade);
            updateOrRemoveColoring(viewableText.parent());
          },

          error: function(data) {
            viewableText.html(oldHtml);
            updateOrRemoveColoring(viewableText.parent());
          }
        });
      }
    });

    $("#assignment_table").on("click", "td[id^='gradeid_']", function() {
      if($("#can_edit").html().trim() == "False") {
        return;
      }

      var i = $(this).find("i");
      if(i.html().trim() == "done") {
        $(this).find("a").attr("data-grade", 0.0);
        i.html("loop");
      }
      else {
        $(this).find("a").attr("data-grade", 1.0);
        i.html("loop");
      }

      $(this).removeClass("success warning error loading");
      $(this).addClass("loading");

      var t = $(this)
      var ids = $(this).attr('id').split('_');
      var csrftoken = getCookie('csrftoken');
      $.ajax({
        beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
        },

        url: $(this).find("a").attr('data-url'),
        data: {
          'grade': $(this).find("a").attr("data-grade")
        },

        method: "POST",
        dataType: 'json',

        success: function(data) {
          if(data.grade == 0) {
            i.html("clear");
          }
          else {
            i.html("done");
          }
          updateOrRemoveColoring(t);
        },

        error: function(data) {
          if($(this).find("a").attr("data-grade") == 0) {
            $(this).find("a").attr("data-grade", 1.0);
            i.html("done");
          }
          else {
            $(this).find("a").attr("data-grade", 0.0);
            i.html("clear");
          }
          updateOrRemoveColoring(t);
        }
      });
    });

    $("#gradebook").on('click', 'td[id^="gradeid_"]', function() {
      if($("#can_edit").html().trim() == "False") {
        return;
      }

      if(highlighted != $(this).attr("id")) {

        highlighted = $(this).attr("id");
        remove_url = $(this).find("a").attr("data-remove-url")
        var a = $(this).find("a").first();

        var text = "<input type=number max=" + $(this).find("a").attr('data-grade-max') +
          " class=\"grade-input\"" +
          " min=" + $(this).find("a").attr('data-grade-min') +
          " step=0.1" +
          " old=\"" + a.html() + "\"" +
          " id=\"" + a.attr("id") + "\"" +
          " title=\"" + a.attr("title") + "\"" +
          " data-url=\"" + $(this).find("a").attr("data-edit-url") + "\"/>";

        if($(this).find("a").attr("data-grade") != "-") {
          text += " <a id=\"remove_grade_a\">" +
              "<i class=\"material-icons float-right\">" +
              "delete_forever" +
              "</i>" +
            " </a>";
        }

        edit = $(text);
        edit.val(a.html());

        edit.keypress(function(event) {
          if (event.keyCode == 13) {
            event.preventDefault();
            edit.blur();
          }
        });

        a.replaceWith(edit);

        $("#remove_grade_a").on("mousedown", function() {
            $("#modal_yes").attr("data-id", highlighted);
            $("#modal_yes").attr("data-url", remove_url);
            $("#modal_yes").attr("func", "remove");
            $("#modal-p").html("Are you sure you want to remove this grade?");
            $("#gradeModal").modal("show");
        });

        edit.focus();
        edit.blur(BlurEdit)
      }
    });

    $("#lowerNum").bind('keyup mouseup', function () {
      if(+$(this).val() <= +$("#upperNum").val()) {
        oldfrom = $(this).val();
        oldto = $("#upperNum").val();
      }
      else {
        oldfrom = $("#upperNum").val();
        oldto = $(this).val();
      }
      updateColoring();
    });

    $("#upperNum").bind('keyup mouseup', function () {
      if(+$(this).val() > +$("#lowerNum").val()) {
        oldto = $(this).val();
        oldfrom = $("#lowerNum").val();
      }
      else {
        oldto = $("#lowerNum").val();
        oldfrom = $(this).val();
      }
      updateColoring();
    });

    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });

    $(".date-picker").datepicker({
        dateFormat: "yy-mm-dd",
        changeMonth: true,
        changeYear: true,
        showAnim: "blind",
        showOptions: {direction: "up"},
        showOn: "button",
        buttonText: "<i class='material-icons'>event</i>"
    });

    function searchTable(searchInput, target2=null) {
        var input, filter, table, tr, tdNumber, tdName, i;
        input = $(searchInput)[0];
        filter = input.value.toLowerCase();
        table = $($(searchInput).data("target"))[0];
        tr = table.getElementsByTagName("tr");

        for (i=0; i < tr.length; i++) {
            if (i <= $($(searchInput).data("target")).data("skip-to-row")) {
                continue;
            }
            tdNumber = tr[i].getElementsByTagName("td")[0];
            tdName = tr[i].getElementsByTagName("td")[1];
            if (tdNumber || tdName) {
                if (tdNumber.innerHTML.toLowerCase().indexOf(filter) > -1 || tdName.innerHTML.toLowerCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }

        if(target2 != null) {
            table = $(target2)[0];
            tr = table.getElementsByTagName("tr");

            for (i=0; i < tr.length; i++) {
                if (i <= $(target2).data("skip-to-row")) {
                    continue;
                }
                tdNumber = tr[i].getElementsByTagName("td")[0];
                tdName = tr[i].getElementsByTagName("td")[1];
                if (tdNumber || tdName) {
                    if (tdNumber.innerHTML.toLowerCase().indexOf(filter) > -1 || tdName.innerHTML.toLowerCase().indexOf(filter) > -1) {
                        tr[i].style.display = "";
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
        }
    }

    $("#searchInput").on('keyup', function() {
        if($(this).data("target2") != "") {
            searchTable(this, $(this).data("target2"));
        }
    });

    var $role_div = $("#form_role_teacher"),
    $module_part_div = $("#form_module_part_teacher"),
    $create_teacher_checkbox = $("#id_create_teacher"),
    $role_teacher = $("#id_role_teacher"),
    $module_part_teacher = $("#id_module_part_teacher");
    // Function that checks for a checked checkbox and changes a form

    $create_teacher_checkbox.change(function() {
       if ($role_teacher.attr('required') && $module_part_teacher.attr('required')) {
           $role_teacher.removeAttr('required');
           $module_part_teacher.removeAttr('required');
       } else {
           $role_teacher.attr('required', 'required');
           $module_part_teacher.attr('required', 'required');
       }
    });

    if ($create_teacher_checkbox.checked) {
        $role_div.show();
        $module_part_div.show();
    }
    $create_teacher_checkbox.change(function() {
        if (this.checked) {
            $role_div.show();
            $module_part_div.show();
        } else {
            $role_div.hide();
            $module_part_div.hide();
        }
    });

    $("#snackbarClose").on('click', function() {
        $("#snackbar").fadeOut(500);
    });

    // Switch the logout menu depending on screen size.
    $(window).on('resize', function() {
        console.log("Window resized");
        var $userDropdown = $("#user-dropdown");
        if ($(window).width() < 992) {
           $userDropdown.removeClass("dropdown-menu-left");
           $userDropdown.addClass("dropdown-menu-right");
        } else {
            $userDropdown.removeClass("dropdown-menu-right");
            $userDropdown.addClass("dropdown-menu-left");
        }
    })
});

// Functions for deleting persons from a module edition
function deleteUser(userpk, studyingspk, url) {
    $.ajax({
        type: 'GET',
        dataType: 'json',
        url: url,
        success: function(response) {
            var success = response['success'],
            personpk = response['person_pk'],
            personName = response['person_name'],
            personNumber = response['person_number'],
            moduleCode = response['module_code'],
            moduleName = response['module_name'],
            $modal = $("#confirmModal" + personpk),
            $messageModal = $("#message" + personpk),
            $snackbar = $("#snackbar"),
            $snackbarMessage = $("#snackbarMessage"),
            message = $messageModal.html();
            if (success) {
                var $tablerow = $("#row" + personpk);
                $modal.modal('hide');
                $tablerow.hide(1000, function() { $tablerow.remove() });
                $snackbarMessage.html(personName + " (" + personNumber +") was successfully removed from module "
                    + moduleName + " (" + moduleCode + ").");
                $snackbar.fadeIn(1000);
            } else {
                $messageModal.html(personName + " (<span class='font-italic'>" + personNumber + "</span>) was <strong>not</strong> deleted from " +
                    moduleName + " (<span class='font-italic'>" + moduleCode + "</span>), because there are still grades in the system for this person.");
            }
            $modal.on('hidden.bs.modal', function() {
                // Resets the modal message
                $messageModal.html(message);
            })
        },
        error: function(xhr, status, errorThrown) {
            console.log(status);
            console.log(errorThrown)
            // Oops, something went wrong
        }
    });

}

jQuery(document).ready(function($) {
  $('[data-toggle="tooltip"]').tooltip();

  if($('#colortoggle').hasClass("coloron")) {
    $('[id^="gradeid_"]').each(function(index) {
      var grade = $(this).find("a").attr("data-grade");
      var mult = $(this).find("a").attr("data-grade-max")/10;
      var color = $(this).attr("data-always-color");

      if(+grade > ((+data.to)*mult)) {
        $(this).removeClass("success warning error loading");
        $(this).addClass("success");
      }
      else if(+grade >= ((+data.from)*mult)){
        $(this).removeClass("success warning error loading");
        $(this).addClass("warning");
      }
      else if(+grade < ((+data.from)*mult)) {
        $(this).removeClass("success warning error loading");
        $(this).addClass("error");
      }
      else if(grade = 'N' && color == 'True') {
        $(this).removeClass("success warning error loading");
        $(this).addClass("error");
      }
    });
  }
});

$('#colortoggle').click(function() {
  if($(this).hasClass("coloron")) {
    $(this).removeClass("coloron");
    $(this).addClass("coloroff");
    $('#coloricon').html("invert_colors");

    $('[id^="gradeid_"]').each(function(index) {
      $(this).removeClass("success warning error loading");
    });
  }
  else {
    $(this).removeClass("coloroff");
    $(this).addClass("coloron");
    $('#coloricon').html("invert_colors_off");

    updateColoring();
  }
});

function updateOrRemoveColoring(select) {
   if($("#colortoggle").hasClass("coloron")) {
      updateColoring();
    }
    else {
      select.removeClass("loading");
    }
}

function updateColoring() {
  if($("#colortoggle").hasClass("coloron")) {
    $('[id^="gradeid_"]').each(function(index) {
      $(this).removeClass("success warning error loading");
      var color = $(this).attr('data-always-color');
      var grade = $(this).find("a").attr("data-grade");
      var mult = $(this).find("a").attr("data-grade-max")/10;

      if($(this).attr("color")) {
        $(this).addClass($(this).attr("color"));
      }
      else if(+grade > ((+oldto)*mult)) {
        $(this).addClass("success");
      }
      else if(+grade >= ((+oldfrom)*mult)){
        $(this).addClass("warning");
      }
      else if(+grade < ((+oldfrom)*mult)) {
        $(this).addClass("error");
      }
      else if(grade = 'N' && color == 'True') {
        $(this).addClass("error");
      }
    });
  }
};