/**
 * Created by 大雄 on 2016/1/16.
 */

var dialog;

function postScript(name, content){
    if (name == "" || content ==""){
        alert("name or content is empty, Please check!");
        return;
    }
    $.post(script_service + "/" + "add", { name: name, content: content }, function(data){
        if (typeof data.ret_code !== 'undefined') {
            if (data.ret_code != 0) {
                alert(data.ret_msg);
            }else{
                $("#script-id").val(data.data.id);
                dialog.dialog( "close" );
            }
        }
    }, dataType="json");
}

function putScript(id, content){
    if (content == ""){
        alert("content is empty, Please check!");
        return;
    }

    $.ajax({
        url:script_service + "/" + id,
        data: { id: id, content: content },
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

function getScript(script_id){
    $.getJSON(script_service + "/" + script_id, function(data){
        var scriptName = $("#script-name");
        if (typeof data.ret_code !== 'undefined') {
            scriptName.val(data.data.name);
            scriptName.attr("readOnly","true");
            $("#script-id").val(script_id);
            $("#script-content").val(showContent(data.data.content));
            dialog.dialog( "open" );
        }
    });
}

function showScriptConsole(script_id) {
    var st = $("select#host-selector");
    st.empty();
    st.multipleSelect({
        single: true,
        width: '80%',
        selectAll: false,
        filter: true,
        style: function(value) {
            return 'text-align:left;';
        }
    });

    var s_url = host_service + "/showall";
    $.getJSON(s_url, function( data ){
        if (typeof data.data !== 'undefined') {
            $.each(data.data, function (key, value) {
                st.append("<option value='" + value.id + "'>" + value.name + "</option>");
            });
            st.multipleSelect('refresh');
            $("#script-id2").val(script_id);
            dialog2.dialog( "open" );
        }else{
            console.log("host_service error");
        }
    });
}

function runScript(script_id, host_id) {
    $.post(script_service + "/" + "runScript", { script_id: script_id, host_id: host_id }, function(data){
        if (typeof data.ret_code !== 'undefined') {
            alert(data.ret_msg);
        }
    }, dataType="json");

    dialog2.dialog( "close" );
}



function showContent(script){
    var lines = Base64.decode(script).split("\n");
    var newscript = "";
    $.each(lines, function(index, line){
        newscript = newscript + eval("'" + line + "'") + "\n";
    });
    return newscript;
}



dialog = $( "#dialog-form" ).dialog({
    dialogClass: "fanui",
    autoOpen: false,
    height: 400,
    width: 600,
    modal: true,
    buttons: {
        "Save Script": function() {
            var scriptId = $("#script-id");
            if (scriptId.val() == "") {
                postScript($("#script-name").val(), $("#script-content").val(), this.dialog);
            }else {
                putScript(scriptId.val(), $("#script-content").val(), this.dialog);
            }
        },
        Cancel: function() {
            dialog.dialog( "close" );
        }
    }
});


dialog2 = $( "#dialog-form2" ).dialog({
    dialogClass: "fanui",
    autoOpen: false,
    height: 400,
    width: 600,
    modal: true,
    buttons: {
        "Run Script": function() {
            var scriptId = $("#script-id2");
            if (scriptId.val() == "") {
                alert("no script selected");
            }else {
                runScript(scriptId.val(), $("select#host-selector").multipleSelect("getSelects").toString());
            }
        },
    }
});

$( "#addInstance" ).click(function (){
    var scriptName = $("#script-name");
    scriptName.val("");
    scriptName.removeAttr("readOnly");
    $("#script-id").val("");
    $("#script-content").val("");
    dialog.dialog( "open" );
});

var from = $("#from");
var to = $("#to");
from.val(formatDate(new Date()));
to.val(formatDate(new Date(new Date().getTime() + day_gap)));
search("Script", from.val(), to.val());

from.datepicker({
    changeMonth: true,
    showButtonPanel: true,
    buttonText: "确定",
    closeText: "取消",
    dateFormat: "yy-mm-dd",
    onClose: function (selectedDate) {
        search("Script", selectedDate, to.val());
        to.datepicker("option", "minDate", selectedDate);
    }
});
to.datepicker({
    defaultDate: "+1w",
    changeMonth: true,
    showButtonPanel: true,
    buttonText: "确定",
    closeText: "取消",
    dateFormat: "yy-mm-dd",
    onClose: function (selectedDate) {
        search("Script", from.val(), selectedDate);
        from.datepicker("option", "maxDate", selectedDate);
    }
});