/**
 * Created by Дѓал on 2016/1/16.
 */

var dialog;

function postServer(name, host, ssh_port, type, port, webapp_home){
    if (name == "" || host =="" || ssh_port =="" || type == "" || webapp_home ==""){
        alert("input is empty, Please check!");
        return;
    }
    $.post(server_service + "/" + "add", { name: name, host: host,
        ssh_port:ssh_port, type:type,
        port:port, webapp_home:webapp_home}, function(data){
        if (typeof data.ret_code !== 'undefined') {
            if (data.ret_code != 0) {
                alert(data.ret_msg);
            }else{
                dialog.dialog( "close" );
            }
        }
    }, dataType="json");
}

function putServer(id, name, host, ssh_port, type, port, webapp_home){
    if (id ==""|| name == "" || host =="" || ssh_port =="" || type == "" || webapp_home ==""){
        alert("input is empty, Please check!");
        return;
    }

    $.ajax({
        url:server_service + "/" + id,
        data: { id: id, name: name, host: host,
            ssh_port:ssh_port, type:type, port:port, webapp_home:webapp_home },
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

function getServer(server_id){
    $.getJSON(server_service + "/" + server_id, function(data){
        if (typeof data.ret_code !== 'undefined') {
            $("#server-id").val(data.data.id);
            $("#server-name").val(data.data.name);
            $("#host-name").val(data.data.host);
            $("#ssh-port").val(data.data.ssh_port);
            $("#server-type").val(data.data.type);
            $("#server-port").val(data.data.port);
            $("#webapp_home").val(data.data.webapp_home);

            dialog.dialog( "open" );
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
        "Save Server": function() {
            var serverId = $("#server-id");
            if (serverId.val() == "") {
                postServer($("#server-name").val(), $("#host-name").val(),
                    $("#ssh-port").val(), $("#server-type").val(),
                $("#server-port").val(), $("#webapp_home").val());
            }else {
                putServer(serverId.val(), $("#server-name").val(), $("#host-name").val(),
                    $("#ssh-port").val(), $("#server-type").val(),
                    $("#server-port").val(), $("#webapp_home").val());
            }
        },
        Cancel: function() {
            dialog.dialog( "close" );
        }
    }
});

$( "#addInstance" ).click(function (){
    var serverName = $("#server-name");
    serverName.val("");
    serverName.removeAttr("readOnly");
    $("#server-id").val("");
    $("#host-name").val("");
    $("#ssh-port").val("");
    $("#server-type").val("");
    $("#server-port").val("");
    $("#webapp_home").val("");
    dialog.dialog( "open" );
});


search("Server");