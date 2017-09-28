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
