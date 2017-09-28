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

var oldfrom = 5
var oldto = 5.5

jQuery(document).ready(function($) {
  $('[data-toggle="tooltip"]').tooltip();

  var changeSlider = function(data) {
  oldto = data.to
  oldfrom = data.from

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
};

$("#colorslider").ionRangeSlider({
        min: 1,
        max: 10,
        from: 5,
        to: 5.5,
        step: 0.1,
        type: 'double',
        grid: true,
        grid_num: 9,
        onChange: changeSlider
    });
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

    $('[id^="gradeid_"]').each(function(index) {
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
});

function searchTable(t, start=0) {
  var input, filter, table, tr, td, i;
  input = document.getElementById("searchTable");
  filter = input.value.toUpperCase();
  table = document.getElementById(t);
  tr = table.getElementsByTagName("tr");

  for (i = start; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}