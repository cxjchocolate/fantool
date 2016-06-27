/**
 * Created by Дѓал on 2016/1/16.
 */

var dialog;

function postHost(name, ip, ssh_port, type){
    if (name == "" || ip =="" || ssh_port =="" || type == ""){
        alert("input is empty, Please check!");
        return;
    }
    $.post(host_service + "/" + "add", { name: name, ip: ip,
        ssh_port:ssh_port, type:type}, function(data){
        if (typeof data.ret_code !== 'undefined') {
            if (data.ret_code != 0) {
                alert(data.ret_msg);
            }else{
                dialog.dialog( "close" );
            }
        }
    }, dataType="json");
}

function putHost(id, name, ip, ssh_port, type){
    if (id == "" ||name == "" || ip =="" || ssh_port =="" || type == ""){
        alert("input is empty, Please check!");
        return;
    }

    $.ajax({
        url:host_service + "/" + id,
        data: { id: id, name: name, ip: ip,
            ssh_port:ssh_port, type:type },
        type: "PUT",
        dataType: "json",
        success:function(data){
            if (typeof data.ret_code !== 'undefined') {
                if (data.ret_code != 0) {
                    alert(data.ret_msg);
                }else{
                    dialog.dialog( "close" );
                }
            }
        }
    });
}

dialog = $( "#dialog-form" ).dialog({
    dialogClass: "fanui",
    autoOpen: false,
    height: 400,
    width: 600,
    modal: true,
    buttons: {
        "Save Host": function() {
            var hostId = $("#host-id");
            if (hostId.val() == "") {
                postHost($("#host-name").val(), $("#host-ip").val(),
                    $("#ssh-port").val(), $("#host-type").val());
            }else {
                putHost(hostId.val(), $("#host-name").val(), $("#host-ip").val(),
                    $("#ssh-port").val(), $("#host-type").val());
            }
        },
        Cancel: function() {
            dialog.dialog( "close" );
        }
    }
});

$( "#addInstance" ).click(function (){
    $("#host-name").val("");
    $("#host-ip").val("");
    $("#ssh-port").val("");
    $("#host-type").val("");
    dialog.dialog( "open" );
});


search("Host");