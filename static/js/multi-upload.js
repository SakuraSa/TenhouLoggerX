$(function() {
    var load_ref = function(index) {
        var tr = $("#command-tr-" + index);
        if(tr.size() <= 0) return true;

        var ref, status;
        var td_list = tr.find("td");
        ref = td_list[1].textContent;
        status = td_list[2].innerText;

        if(status != "uploaded") {
            td_list[2].innerHTML = '<i class="fa fa-refresh fa-spin"></i> 上传中...';
            td_list[2].className = "";
            $.get("/api/upload_ref?ref=" + ref, function(data, status) {
               if(data.ok && data.status == 'ok') {
                   td_list[1].innerHTML = '<a href="/' + ref + '">' + ref + '</a>';
                   td_list[2].innerHTML = '<i class="fa fa-check"></i> 已上传';
                   td_list[2].className = "success";
               }else {
                   td_list[2].innerHTML = '<i class="fa fa-times"></i> ' + data.status;
                   td_list[2].className = "danger";
               }
               load_ref(index + 1);
            });
            return true;
        }else {
            return load_ref(index + 1);
        }
    };

    load_ref(0);
});
