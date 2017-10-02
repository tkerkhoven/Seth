var oldto = 5.5;
var oldfrom = 5;
var searchString = "";

$(".btn").mouseup(function(){
    $(this).blur();
})

$(document).ready(function() {
    $('#parent').on('change',function(){
      $('.child').prop('checked',$(this).prop('checked'));
    });
    $('.child').on('change',function(){
      $('#parent').prop('checked',$('.child:checked').length == $('.child').length);
    });
});

jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
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
    var searchSplit = searchTerm.replace(/ /g, "'):containsi('");

    var re = /[><][0-9]+%/;
    if(searchSplit.search(re) != -1) {
        var [bt,num] = getNum(searchSplit);

        if(num >= 0 && num <= 100) {
            $('[id^="gradeid_"]').each(function(index) {
                var grade = $(this).attr("data-grade");
                var check = ($(this).attr("data-grade-max")/100)*num;

                if((bt)?(grade >= check):(grade <= check)) {
                    if($(this).closest('tr').index() > skipToRow)
                        $(this).closest('tr').show();
                }
                else {
                    if($(this).closest('tr').index() > skipToRow)
                        $(this).closest('tr').hide();
                }
            });
        }
    }
    else {
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
    }
  });
});


var getNum = function(str) {
    var bt = false;
    var num = 0;
    if(str.startsWith('>')) {
        bt = true;
    }
    num = parseInt(str.substring(1,str.length-1));
    return [bt, num];
};