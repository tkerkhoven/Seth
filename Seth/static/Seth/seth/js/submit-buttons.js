$(document).ready(function() {
    $("#addUserLink").on('click', function() {
        $("#addUser").submit();
    });

    $("#updateUserLink").on('click', function() {
        $("#updateUser").submit();
    });

    $("#removeUserLink").on('click', function() {
        $("#removeUser").submit();
    });

    $("#updateUserSave").on('click', function() {
        $("#updateUserForm").submit();
    });

    $("#createPersonSave").on('click', function() {
        $("#createPersonForm").submit();
    });
});