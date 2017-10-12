var oldto = 5.5;
var oldfrom = 5;
var searchString = "";

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
      updateColoring();
    });

    table.on('draw', function() {
      updateColoring();
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
      updateColoring()
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
      updateColoring()
    });

    $('#parent').on('change',function(){
      $('.child').prop('checked',$(this).prop('checked'));
    });
    $('.child').on('change',function(){
      $('#parent').prop('checked',$('.child:checked').length == $('.child').length);
    });

    $("#addUserLink").on('click', function() {
        $("#addUser").submit();
    });

    $("#updateUserLink").on('click', function() {
        $("#updateUser").submit();
    });

    $("#removeUserLink").on('click', function() {
        $("#removeUser").submit();
    });

    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });


    $("#searchInput").on('keyup', function() {
       var input, filter, table, tr, td, i;
        input = $("#searchInput")[0];
        filter = input.value.toLowerCase();
        table = $("#personTable")[0];
        tr = table.getElementsByTagName("tr");

        for (i=0; i < tr.length; i++) {
            td = tr[i].getElementsByTagName("td")[2];
            if (td) {
                if (td.innerHTML.toLowerCase().indexOf(filter) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none"
                }
            }
        }
    });
});

jQuery(document).ready(function($) {
  $('[data-toggle="tooltip"]').tooltip();

  if($('#colortoggle').hasClass("coloron")) {
    $('[id^="gradeid_"]').each(function(index) {
      var grade = $(this).attr("data-grade")
      var mult = $(this).attr("data-grade-max")/10

      if(+grade > ((+data.to)*mult)) {
        $(this).removeClass("success warning error")
        $(this).addClass("success")
      }
      else if(+grade >= ((+data.from)*mult)){
        $(this).removeClass("success warning error")
        $(this).addClass("warning")
      }
      else if(+grade < ((+data.from)*mult)) {
        $(this).removeClass("success warning error")
        $(this).addClass("error")
      }
    });
  }
});

$('#colortoggle').click(function() {
  if($(this).hasClass("coloron")) {
    $(this).removeClass("coloron")
    $(this).addClass("coloroff")
    $('#coloricon').html("invert_colors")

    $('[id^="gradeid_"]').each(function(index) {
      $(this).removeClass("success warning error")
    });
  }
  else {
    $(this).removeClass("coloroff")
    $(this).addClass("coloron")
    $('#coloricon').html("invert_colors_off")

    updateColoring()
  }
});

function updateColoring() {
  if($("#colortoggle").hasClass("coloron")) {
    $('[id^="gradeid_"]').each(function(index) {
      $(this).removeClass("success warning error")
      var grade = $(this).attr("data-grade")
      var mult = $(this).attr("data-grade-max")/10

      if(+grade > ((+oldto)*mult)) {
        $(this).addClass("success")
      }
      else if(+grade >= ((+oldfrom)*mult)){
        $(this).addClass("warning")
      }
      else if(+grade < ((+oldfrom)*mult)) {
        $(this).addClass("error")
      }
    });
  }
};