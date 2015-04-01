$(function(){
  var input_group = $("#ver-code-input-group");
  var ver_code_input = input_group.find("#ver_code");
  var ver_uuid_input = input_group.find("#ver_uuid");
  var container = $("#ver-code-container");
  var image = container.find("#ver_image");
  var reload_function = function () {
    image.attr('src', '/static/image/icon/loading.gif');
    $.get('/api/create_verification_code', function(code, status) {
      ver_uuid_input.val(code.uuid);
      ver_code_input.val('');
      image.attr('src', code.image);
      input_group.removeClass('has-error').removeClass('has-success');
      input_group.remove("span");
    });
  };
  image.click(function() {
    reload_function();
    ver_code_input.focus();
  });
  ver_code_input.popover({
    trigger:"manual",
    title:"验证码",
    html:true,
    placement:"top",
    content:container
  });
  var ready_to_hide = false;
  ver_code_input.focus(function () {
    ready_to_hide = false;
    if(!ver_code_input.attr('readonly'))
      ver_code_input.popover('show');
  });
  ver_code_input.blur(function () {
    ready_to_hide = true;
    setTimeout(function(){
      if(ready_to_hide) {
        ver_code_input.popover('hide');
        ready_to_hide = false;
      }
    }, 1000);
  });
  ver_code_input.blur(function () {
    ver_code_input.val(ver_code_input.val().toUpperCase().replace(/[^ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890]/g, ""));
    if(ver_code_input.val().length == ver_code_input.attr('maxlength')) {
      $.get("/api/check_verification_code?ver_uuid=" + ver_uuid_input.val() +"&ver_code=" + ver_code_input.val(), function(result, status) {
        if(result["ok"]) {
          input_group.addClass('has-success');
          input_group.append($("span").attr("class", "glyphicon glyphicon-ok form-control-feedback"));
          ver_code_input.attr("readonly", "true");
        }else {
          input_group.addClass('has-error');
          input_group.append($("span").attr("class", "glyphicon glyphicon-remove form-control-feedback"));
        }
      })
    }
  });
});