/**
 * Created by 大雄 on 2016/1/16.
 */

var dialog;

function postApp(brand, app, master_svn, config_svn, context, servers, cdn_type, domainId, url){
    if (brand == "" || app =="" || master_svn == "" || context == "" || servers == ""){
        alert("some is empty, Please check!");
        return;
    }
    if (!(cdn_type === undefined || cdn_type == "no")){
        if (domainId == "" || url == ""){
            alert("information about CDN is empty, Please check!");
            return;
        }
    }else{
        cdn_type = "no";//don't use undefined value
    }

    $.post(app_service + "/" + "add",
        { brand: brand, app: app,
            master_svn: master_svn, config_svn:config_svn,
            context:context, servers:servers,
            cdn_type:cdn_type, domainId:domainId,url:url }, function(data){
        if (typeof data.ret_code !== 'undefined') {
            if (data.ret_code != 0) {
                alert(data.ret_msg);
            }else{
                $("#app-id").val(data.data.id);
                dialog.dialog( "close" );
            }
        }
    }, dataType="json");
}

function putApp(id, master_svn, config_svn, context, servers, cdn_type, domainId, url){
    if (id == "" || master_svn == "" || context == "" || servers == ""){
        alert("some is empty, Please check!");
        return;
    }
    if (!(cdn_type === undefined || cdn_type == "no")){
        if (domainId == "" || url == ""){
            alert("information about CDN is empty, Please check!");
            return;
        }
    }else{
        cdn_type = "no";//don't use undefined value
    }
    $.ajax({
        url:app_service + "/" + id,
        data: { id: id, master_svn: master_svn, config_svn:config_svn,
            context:context, servers:servers,
            cdn_type:cdn_type, domainId:domainId,url:url},
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

function getApp(app_id){
    $.getJSON(app_service + "/" + app_id, function(data){
        if (typeof data.ret_code !== 'undefined') {
            var brand = $("#brand-name");
            var app = $("#app-name");
            brand.attr("readOnly","true");
            brand.val(data.data.brand);
            app.attr("readOnly","true");
            app.val(data.data.app);
            $("#app-id").val(app_id);
            $("#master-svn").val(data.data.configs.MASTER_SVN);
            $("#config-svn").val(data.data.configs.CONFIG_SVN);
            $("#context").val(data.data.configs.CONTEXT);

            var servers = data.data.configs.SERVERS.split(",");
            showServerSelector(servers);

            var check_val = data.data.configs.CDN_TYPE;
            console.log(check_val);
            var e = "input[name='refreshcdn'][value=" + "'" + check_val + "']";
            $(e).attr("checked",true);

            $("tr#tr-domainId").val(data.data.configs.DOMAINID);
            $("tr#tr-url").val(data.data.configs.URL);

            if (check_val == "ucdn"){
                $("tr#tr-domainId").css('display','');
                $("tr#tr-url").css('display','');
            }else{
                $("tr#tr-domainId").css('display','none');
                $("tr#tr-url").css('display','none');
            }

            dialog.dialog( "open" );
        }
    });
}

function showServerSelector(selectedServers){

    var serverSelector = $("#server-selector");
    serverSelector.empty();

    var s_url = server_service + "/showall";
    $.getJSON(s_url, function( data ){
        if (typeof data.data !== 'undefined') {
            $.each(data.data, function (key, value) {
                serverSelector.append("<option value='" + value.id + "'>" + value.name + "</option>");
            });
            serverSelector.multipleSelect('refresh');
            if (typeof selectedServers !== 'undefined') {
                serverSelector.multipleSelect("setSelects", selectedServers);
            }
        }else{
            console.log("server_service error");
        }
    });
}

search("App");

dialog = $( "#dialog-form" ).dialog({
    dialogClass: "fanui",
    autoOpen: false,
    height: 600,
    width: 600,
    modal: false,
    stack: false,
    buttons: {
        "Save App": function() {
            var appid = $("#app-id");
            if (appid.val() == "") {
                postApp($("#brand-name").val(), $("#app-name").val(),
                    $("#master-svn").val(), $("#config-svn").val(),
                    $("#context").val(), $("#server-selector").multipleSelect("getSelects").toString(),
                    $("input[name='refreshcdn']:checked").val(), $("tr#tr-domainId").val(), $("tr#tr-url").val());
            }else {
                putApp(appid.val(), $("#master-svn").val(), $("#config-svn").val(),
                    $("#context").val(), $("#server-selector").multipleSelect("getSelects").toString(),
                    $("input[name='refreshcdn']:checked").val(), $("#domainId").val(), $("#url").val());
            }
        },
        Cancel: function() {
            dialog.dialog( "close" );
        }
    }
});

$( "#addInstance" ).click(function (){
    var brand = $("#brand-name");
    brand.val("");
    brand.removeAttr("readOnly");
    var app = $("#app-name");
    app.val("");
    app.removeAttr("readOnly");

    $("#master-svn").val("");
    $("#config-svn").val("");
    $("#context").val("");
    showServerSelector();
    dialog.dialog( "open" );
});

$('#server-selector').multipleSelect({
    width: '80%',
    selectAll: false,
    filter: true,
    position: 'top',
    style: function(value) {
        return 'text-align:left;';
    }
});

$("input[name='refreshcdn']").change(function() {
    var check_val = $("input[name='refreshcdn']:checked").val();
    if (check_val == "ucdn"){
        $("tr#tr-domainId").css('display','');
        $("tr#tr-url").css('display','');
    }else{
        $("tr#tr-domainId").css('display','none');
        $("tr#tr-url").css('display','none');
    }
});
