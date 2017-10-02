var oldto = 5.5;
var oldfrom = 5;
var searchString = "";

$(".btn").mouseup(function(){
    $(this).blur();
});

$(document).ready(function() {
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
      console.log("D");
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
      console.log("F");
    });
  }
};

$(document).ready(function() {
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
      oldfrom = $(this).val();
      oldto = $("#upperNum").val();
    }
    else {
      oldfrom = $("#upperNum").val();
      oldto = $(this).val();
    }
    updateColoring()
  });

  $("#searchTable").keyup(function () {
    var searchTerm = $("#searchTable").val();
    var listItem = $('#gradebook tbody').children('tr');
    var skipToRow = $('#gradebook').attr("data-skip-to-row");
    var searchSplit = searchTerm.replace(/ /g, "'):containsi('")

    $.extend($.expr[':'], {
      'containsi': function(elem, i, match, array){
        return (elem.textContent || elem.innerText || '').toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
      }
    });

    $("#gradebook tbody tr").not(":containsi('" + searchSplit + "')").each(function(e){
      if($(this).index() > skipToRow) {
        $(this).hide();
      }
    });

    $("#gradebook tbody tr:containsi('" + searchSplit + "')").each(function(e){
      if($(this).index() > skipToRow) {
        $(this).show();
      }
    });
  });
});