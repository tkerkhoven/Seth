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

function updateSearchResults() {
  $("#gradebook tbody tr").not(":containsi('" + searchString + "')").each(function(e){
    if($(this).index() > 1) {
      $(this).hide();
    }
  });

  $("#gradebook tbody tr:containsi('" + searchString + "')").each(function(e){
    if($(this).index() > 1) {
      $(this).show();
    }
  });
}

$(document).ready(function() {
  $("#lowerNum").bind('keyup mouseup', function () {
    if($(this).val() <= $("#upperNum").val()) {
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
    if($(this).val() > $("#lowerNum").val()) {
      oldfrom = $(this).val();
      oldto = $("#upperNum").val();
    }
    else {
      oldfrom = $("#upperNum").val();
      oldto = $(this).val();
    }
    updateColoring()
  });

  $("#searchTable").keypress(function (e) {
    if(e.which == 13) {
      var searchTerm = $("#searchTable").val();
      var listItem = $('#gradebook tbody').children('tr');
      var searchSplit = searchTerm.replace(/ /g, "'):containsi('")

      $.extend($.expr[':'], {
        'containsi': function(elem, i, match, array){
          return (elem.textContent || elem.innerText || '').toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
        }
      });

      searchString = searchString + " " + searchSplit;

      var $badge = $('div[id^="badge"]:last');
      var num = parseInt( $badge.prop("id").match(/\d+/g), 10 ) +1;
      var $clone = $badge.clone().prop('id', 'badge'+num );
      $badge.after( $clone.text('klon'+num) );

      $clone.html(searchSplit + " X");
      $clone.click(function() {
        var s = $clone.html().replace(/\sX(?!.*\sX)/, "");
        searchString = searchString.replace(new RegExp(s + "(?!.*" + s + ")"), "");
        updateSearchResults();
        $clone.remove();
      });
      $clone.show();

      $("#searchTable").val("");

      updateSearchResults();
    }
  });
});