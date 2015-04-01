$(function () {
    var inputUsername = $('input[name="username"]');
    var inputPassword = $('input[name="password"]');

    var set_normal = function(inputObj) {
        var parent = inputObj.parent();
        parent.removeClass('has-success').removeClass('has-error');
        parent.remove("span");
    };

    var set_success = function(inputObj) {
        var parent = inputObj.parent();
        parent.addClass("has-success");
        parent.append($("span").attr("class", "glyphicon glyphicon-ok form-control-feedback"));
    };

    var set_error = function(inputObj) {
        var parent = inputObj.parent();
        parent.addClass("has-error");
        parent.append($("span").attr("class", "glyphicon glyphicon-remove form-control-feedback"));
    };

    var validate = function(inputObj, func) {
        inputObj.blur(function() {
            func(inputObj);
        });
        inputObj.change(function() {
            set_normal(inputObj);
        })
    };

    validate(inputUsername, function() {
        var username = inputUsername.val();
        $.get('/api/get_username_availability?username=' + username, function (data, status) {
            if(!data['availability']) {
                set_success(inputUsername);
            }else {
                set_error(inputUsername);
            }
        });
    });

    validate(inputPassword, function() {
        var password = inputPassword.val();
        if(password) {
            set_success(inputPassword);
        }else {
            set_error(inputPassword);
        }
    });
});