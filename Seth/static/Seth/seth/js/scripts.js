var oldto = 5.5;
var oldfrom = 5;
var searchString = "";
var changed = [];

$(".btn").mouseup(function(){
    $(this).blur();
});

function BlurEdit() {
    var text = $(this).val();
    var viewableText = $("<a></a>");
    viewableText.html(text);
    viewableText.attr('id', $(this).attr('id'));
    viewableText.attr('title', $(this).attr('title'));
    $(this).replaceWith(viewableText);
};

$(document).ready(function() {

    $('[id^="collapsePart"').on('show.bs.collapse', function () {
      var id = $(this).attr("data-id");
      $("#mp_collapse" + id).find("i").html("arrow_drop_up");
    })
    $('[id^="collapsePart"').on('hide.bs.collapse', function () {
      var id = $(this).attr("data-id");
      $("#mp_collapse" + id).find("i").html("arrow_drop_down");
    })

    $('[data-toggle="popover"]').each( function() {
      $(this).popover({
                        html : true,
                        content: '<a id="remove_grade_a" data-url="' + $(this).attr("data-url") + '" data-toggle="modal" data-target="#gradeRemoveModal">' +
                                   '<i class="material-icons float-right">' +
                                     'delete_forever' +
                                   '</i>' +
                                 '</a>',
                        placement: "bottom"
                     });
    });

    $('#gradeRemoveModal').on('show.bs.modal', function(e) {
      var url = $(e.relatedTarget).data('url');
      $(e.currentTarget).find('form[id="remove_grade_yes"]').attr("action", url);
    });

    $('th:has(a.expandable)').addClass('dashed');

    $("#assignment_table").on("click", "td[id^='gradeid_']", function() {
      var i = $(this).find("i");
      if(i.html().trim() == "done") {
        $(this).attr("data-grade", 0.0);
        i.html("clear");
      }
      else {
        $(this).attr("data-grade", 1.0);
        i.html("done");
      }

      var ids = $(this).attr('id').split('_');
      var removed = false;

      if(changed.length > 0) {
        for( i=changed.length-1; i>=0; i--) {
          if( changed[i].sid == ids[1] && changed[i].assign == ids[2]) {
            changed.splice(i,1);
            removed = true;
            break;
          }
        }
      }

      if(!removed)
        changed.push({sid: ids[1], assign: ids[2]});

      updateColoring();
    });

    /*
    Grade click change
    $(document).on('click', 'a[id^="grade_"]', function() {

      var edit = $("<input type=number max=" + $(this).parent().closest('td').attr('data-grade-max') +
        " min=" + $(this).parent().closest('td').attr('data-grade-min') +
        " step=0.25/>");
      edit.val($(this).html());
      edit.attr('id', $(this).attr('id'));
      edit.attr('title', $(this).attr('title'));

      edit.keypress(function(event) {
        if (event.keyCode == 13) {
          event.preventDefault();
          edit.blur();
        }
      });

      $(this).replaceWith(edit);
      edit.focus();
      edit.blur(BlurEdit)
    });
    */

    $('a[data-toggle="tab"]').on( 'shown.bs.tab', function (e) {
        $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
    } );

    var table = $('#gradebook').DataTable({
      "ordering": true,
      "order": [[0, 'asc']],
      "columnDefs": [{
        orderable: false,
        targets: "no-sort"
      }],

      drawCallback: function(settings){
        var api = this.api();

        $('td', api.table().container()).tooltip({
           container: 'body'
        });
      }
    });

    var assignmenttable = $('#assignment_table').DataTable({
      "ordering": true,
      "order": [[0, 'asc']],
      "columnDefs": [
        {orderable: false, targets: "no-sort"},
        {visible: false, targets: "remove"}
      ],

      drawCallback: function(settings){
        var api = this.api();

        $('td', api.table().container()).tooltip({
           container: 'body'
        });
      }
    });

    var studenttable = $('#studentbook').DataTable({
      "ordering": false,
      "paging": false,
      "searching": false,

      drawCallback: function(settings){
        var api = this.api();

        $('td', api.table().container()).tooltip({
           container: 'body'
        });
      }
    });

    var studenttable = $('#studentbook_assignments').DataTable({
      "ordering": false,
      "paging": false,
      "searching": false,
      "columnDefs": [
        {visible: false, targets: "remove"}
      ],

      drawCallback: function(settings){
        var api = this.api();

        $('td', api.table().container()).tooltip({
           container: 'body'
        });
      }
    });

    studenttable.on('draw', function() {
      studenttable.columns('.remove').each(function() {
        ($(this).visible(false));
      });
    });

    var testtable = $('#testbook').DataTable({
      "paging": false,
      "ordering": true,
      "order": [[1, 'asc']],
      "columnDefs": [{
        orderable: false,
        targets: "no-sort"
      }],

      drawCallback: function(settings){
        var api = this.api();

        $('td', api.table().container()).tooltip({
           container: 'body'
        });
      }
    });

    testtable.on('draw', function() {
      $('[data-toggle="popover"]').popover();
      updateColoring();
    });

    assignmenttable.on('draw', function() {
      $('[data-toggle="popover"]').popover();
      updateColoring();
    });

    table.on('draw', function() {
      $('[data-toggle="popover"]').popover();
      updateColoring();
    })

    $(".expandable").click(function() {
      name = $(this).attr("data-original-name");
      $(this).attr("data-original-name", $(this).html())
      $(this).html(name);

      if($(this).attr("data-expanded") == 0) {
        $(this).attr("data-expanded", 1);
        $(this).parent().addClass("dashed");
        studenttable.columns(".remove").visible(false);
      }
      else {
        $(this).attr("data-expanded", 0);
        $(this).parent().removeClass("dashed");
        studenttable.columns('.remove').visible(true);
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

    $('#parent').on('change',function(){
      $('.child').prop('checked',$(this).prop('checked'));
    });
    $('.child').on('change',function(){
      $('#parent').prop('checked',$('.child:checked').length == $('.child').length);
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


    $("#searchInput").on('keyup', function() {
       var input, filter, table, tr, tdNumber, tdName, i;
        input = $("#searchInput")[0];
        filter = input.value.toLowerCase();
        table = $("#personTable")[0];
        tr = table.getElementsByTagName("tr");

        for (i=0; i < tr.length; i++) {
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
    });

    // $("#label_role").hide();
    // $("#label_module_part").hide();
    // $("#id_role").hide();
    // $("#id_module_part").hide();
    var $role_div = $("#form_role_teacher"),
    $module_part_div = $("#form_module_part_teacher"),
    $create_teacher_checkbox = $("#id_create_teacher");
    // Function that checks for a checked checkbox and changes a form
    if ($create_teacher_checkbox.checked) {
        $role_div.show();
        $module_part_div.show();
    }
    $create_teacher_checkbox.change(function() {
        if (this.checked) {
            // $("#id_role").show();
            // $("#label_role").show();
            // $("#id_module_part").show();
            // $("#label_module_part").show();
            $role_div.show();
            $module_part_div.show();
        } else {
            // $("#id_role").hide();
            // $("#label_role").hide();
            // $("#id_module_part").hide();
            // $("#label_module_part").hide();
            $role_div.hide();
            $module_part_div.hide();
        }
    })
});

jQuery(document).ready(function($) {
  $('[data-toggle="tooltip"]').tooltip();

  if($('#colortoggle').hasClass("coloron")) {
    $('[id^="gradeid_"]').each(function(index) {
      var grade = $(this).attr("data-grade");
      var mult = $(this).attr("data-grade-max")/10;
      var color = $(this).attr("data-always-color");

      if(+grade > ((+data.to)*mult)) {
        $(this).removeClass("success warning error");
        $(this).addClass("success");
      }
      else if(+grade >= ((+data.from)*mult)){
        $(this).removeClass("success warning error");
        $(this).addClass("warning");
      }
      else if(+grade < ((+data.from)*mult)) {
        $(this).removeClass("success warning error");
        $(this).addClass("error");
      }
      else if(grade = 'N' && color == 'True') {
        $(this).removeClass("success warning error");
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
      $(this).removeClass("success warning error");
    });
  }
  else {
    $(this).removeClass("coloroff");
    $(this).addClass("coloron");
    $('#coloricon').html("invert_colors_off");

    updateColoring();
  }
});

function updateColoring() {
  if($("#colortoggle").hasClass("coloron")) {
    $('[id^="gradeid_"]').each(function(index) {
      $(this).removeClass("success warning error");
      var color = $(this).attr('data-always-color');
      var grade = $(this).attr("data-grade");
      var mult = $(this).attr("data-grade-max")/10;

      if(+grade > ((+oldto)*mult)) {
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