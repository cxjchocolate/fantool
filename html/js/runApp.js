function infoApp(e) {
    var obj = $(e.currentTarget);
    console.log(e);
    var dialog = Dialog.getSingleton();
    dialog.setContent('<i class="icon-spinner icon-spin icon-4x"></i>');
    var offset = obj.offset();
    //alert("btn:" + offset.left + "," + offset.top);
    //dialog.showInfo();
    dialog.setPosition(offset.left + (obj.width() - dialog.width()) / 2, offset.top + obj.height() + dialog.height());
    dialog.show();
    //异步查询app的详细信息
    var s_url = app_info_service + "/" + e.currentTarget.dataset.brand + "/" + e.currentTarget.dataset.app;
    $.getJSON(s_url, function (data) {
        var items = [];
        if (typeof data.data !== 'undefined') {
            $.each(data.data, function (key, value) {
                if (key.toUpperCase() == 'BUILDXML') {
                    items.push('<li class="app-info-item" id="' + key + '"><b>' + key + ":</b> " + '<a href="' + conf_service + "/" + value + '" target="_blank">' + value + '</a></li>');
                } else {
                    items.push('<li class="app-info-item" id="' + key + '"><b>' + key + ":</b> " + value + "</li>");
                }
            });
            dialog.setContent('<ul class="app-info-list">' + items.join("") + "</ul>");
        } else {
            dialog.setContent('<i class="icon-warning-sign icon-4x"></i>')
        }
    })
        .fail(function () {
            console.log("error");
            dialog.setContent("error");
        });
}

function flushmem(brand, res) {
    var s_url = mem_flush_service + "/" + brand + "/" + res;
    $.getJSON(s_url, function (data) {
        conlog(data.ret_msg);
    });
}

function keysmem(brand, res) {
    var s_url = mem_keys_service + "/" + brand + "/" + res;
    $.getJSON(s_url, function (data) {
        var items = [];
        if (typeof data.data !== 'undefined') {
            $.each(data.data, function (index, value) {
                items.push("<li id='" + index + "'>" + value + "</li>");
            });
        }
        $("<ol/>", {
            "class": "my-new-list",
            html: items.join("")
        }).appendTo($("#console"));
    });
}

function clearConsole() {
    $("#console").html("")
}

function conlog(msg) {
    var o = $("#console");
    o.append(msg + "<br>");
    //$("#console").scrollHeight undefined
    o.scrollTop(document.getElementById("console").scrollHeight);
}

function Terminal() {
    var terms = [];
    Terminal.prototype.addTerm = function (e) {
        var obj = $(e.currentTarget);
        var attr_onclick = obj.attr("onclick");
        obj.attr("onclick", "");
        var ws = new WebSocket(ws_url);
        var dt = new Date();
        ws.term_id = dt.valueOf();
        ws.target = obj;
        ws.target_onclick = attr_onclick;
        ws.term_status = "init";
        console.log(e.currentTarget.dataset);
        var json = '';
        if (e.currentTarget.dataset.action == 'deployApp') {
            //json = '{"data":{"action":"' + e.currentTarget.dataset.action + '","brand":"' + e.currentTarget.dataset.brand + '","app":"' + e.currentTarget.dataset.app + '"}}';
            showSVNSelector(e.currentTarget.dataset.brand, e.currentTarget.dataset.app);
            return;
        }
        if (e.currentTarget.dataset.action == 'standard-deploy') {
            json = '{"data":{"action":"' + e.currentTarget.dataset.action + '","brand":"' + e.currentTarget.dataset.brand + '","app":"' + e.currentTarget.dataset.app + '","master_svn":"' + e.currentTarget.dataset.master_svn + '","config_svn":"' + e.currentTarget.dataset.config_svn + '"}}';
        }
        if (e.currentTarget.dataset.action == 'packApp'){
            json = '{"data":{"action":"' + e.currentTarget.dataset.action + '","buildxml":"' + e.currentTarget.dataset.buildxml + '","version":"' + e.currentTarget.dataset.version + '"}}';
        }
        if (e.currentTarget.dataset.action == 'restartServer'){
            json = '{"data":{"action":"' + e.currentTarget.dataset.action + '","brand":"' + e.currentTarget.dataset.brand + '","res":"' + e.currentTarget.dataset.res + '"}}';
        }
        ws.term_name = json;
        terms.push(ws);
        var item_li = $("<li/>",{
            "class":"task-item",
            "id":ws.term_id
        });
        var item_name_span = $("<span/>",{
           "class":"task-name",
            "html": ws.term_name
        });
        item_li.append('<i class="icon-refresh icon-spin task-status-ok"></i>');
        item_li.append(item_name_span);
        item_li.appendTo($("#task-list"));

        ws.onopen = function (event) {
            console.log(this.term_name);
            ws.send(this.term_name);
            this.term_status = 'open';
        };
        ws.onclose = function (event) {
            console.log("message:socket onclose");
            var child = $('#' + this.term_id + ' i:first');
            if (this.term_status == "success") {
                child.removeClass("icon-refresh icon-spin");
                child.addClass("icon-ok");
            }else {
                child.removeClass("icon-refresh icon-spin task-status-ok");
                child.addClass("icon-remove task-status-error");
            }
            this.term_status = "closed";
            //恢复div onclick
            this.target.attr("onclick", this.target_onclick);
        };
        ws.onerr = function (event) {
            console.log("message:socket onerr");
            $("<i/>", {"class": "icon-remove task-status"}).appendTo($('#' + this.term_id));
            this.term_status = 'error';
            //恢复div onclick
            this.target.attr("onclick", this.target_onclick);

        };
        ws.onmessage = function (event) {
            var obj = $.parseJSON(event.data);

            if (obj.ret_code === 'success' || obj.ret_code === 'error') {
                //EOF of command
                this.close();
                this.term_status = obj.ret_code
            }else{conlog(obj.ret_msg);}
        };
    }
}

function showSVNSelector(brand, app){

    var container = $("#brand-selector-container");
    var brandselect = $("#brandselect");
    var appselect = $("#appselect");
    var masterSvnselect = $("#masterSvnselect");
    var configSvnselect = $("#configSvnselect");
    var sd = document.getElementById('standard-deploy');

    sd.dataset.brand = brand;
    sd.dataset.app   =  app ;
    brandselect.html("<option value='" + brand + "'>" + brand + "</option>");
    appselect.html("<option value='" + app + "'>" + app + "</option>");
    masterSvnselect.empty();
    configSvnselect.empty();
    container.show();

    var s_url = svn_log_service + "/" + brand + "/" + app;
    $.getJSON(s_url, function( data ){
        if (typeof data.data !== 'undefined') {
            var master_svn_logentries = data.data.MASTER_SVN_LOG;
            var config_svn_logentries = data.data.CONFIG_SVN_LOG;

            $.each(master_svn_logentries, function (key, value) {
                masterSvnselect.append("<option value='" + value[0] + "'>" + value[0] + "</option>");
            });
/*            masterSvnselect.change(function(){
                sd.dataset.master_svn = masterSvnselect.val();
            });*/

            if (typeof config_svn_logentries !== 'undefined'){
                $.each(config_svn_logentries, function (key, value) {
                    configSvnselect.append("<option value='" + value[0] + "'>" + value[0] + "</option>");
                });
/*                configSvnselect.change(function(){
                    sd.dataset.config_svn = configSvnselect.val();
                });*/
            }
        }else{
            console.log("svn_log_service error");
        }
    });
}

function standardDeploy(event){
    var masterSvnselect = $("#masterSvnselect");
    var configSvnselect = $("#configSvnselect");
    var sd = document.getElementById('standard-deploy');

    sd.dataset.master_svn = masterSvnselect.val();
    sd.dataset.config_svn = configSvnselect.val();

    if ((masterSvnselect.val() == null ) && (configSvnselect.val() == null || $("#configSvnselect option").length == 0)){
        alert("svn log is not selected!");
    }else {
        var container = $("#brand-selector-container");
        container.hide();
        ts.addTerm(event);
    }
}