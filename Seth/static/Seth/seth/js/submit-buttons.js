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

    $("#createModuleEdSave").on('click', function() {
        $("#createModuleEdForm").submit();
    });

    $("#updateModuleEdSave").on('click', function() {
        $("#updateModuleEdForm").submit();
    });

    $("#createModulePartSave").on('click', function() {
        $("#createModulePartForm").submit();
    });

    $("#updateModulePartSave").on('click', function() {
        $("#updateModulePartForm").submit();
    });

    $("#createTestSave").on('click', function() {
        $("#createTestForm").submit();
    });

    $("#updateTestSave").on('click', function() {
        $("#updateTestForm").submit();
    });
});