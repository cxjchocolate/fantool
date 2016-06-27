function showScriptSelector(st, selectedScripts){

    st.empty();
    st.multipleSelect({
        single: true,
        width: '80%',
        selectAll: false,
        filter: true,
        style: function(value) {
            return 'text-align:left;'
        }
    });

    var s_url = script_service + "/showall";
    $.getJSON(s_url, function( data ){
        if (typeof data.data !== 'undefined') {
            $.each(data.data, function (key, value) {
                st.append("<option value='" + value.id + "'>" + value.name + "</option>");
            });
            st.multipleSelect('refresh');
            if (typeof selectedScripts !== 'undefined') {
                st.multipleSelect("setSelects", selectedScripts);
            }
        }else{
            console.log("script_service error");
        }
    });
}

function showHostSelector(st, selectedHosts){

    st.empty();
    st.multipleSelect({
        width: '80%',
        selectAll: false,
        filter: true,
        style: function(value) {
            return 'text-align:left;'
        },
        disabledClass:'enabled'
    });

    var s_url = host_service + "/showall";
    $.getJSON(s_url, function( data ){
        if (typeof data.data !== 'undefined') {
            $.each(data.data, function (key, value) {
                st.append("<option value='" + value.id + "'>" + value.name + "</option>");
            });
            st.multipleSelect('refresh');
            if (typeof selectedHosts !== 'undefined') {
                st.multipleSelect("setSelects", selectedHosts);
            }
        }else{
            console.log("host_service error");
        }
    });
}

function Job(parent) {

    var job_container =  $("<div class='job-container'>");
    var job_header    =  $('<div class="job-header">\
                                <label>Job Name: </label>\
                                <input type="text" name="job-name" id="job-name">\
                                <input type="hidden" name="job-id" id="job-id">\
                            </div>');
    var job_body      =  $("<div class='job-body'>");
    var job_tailor    =  $('<div class="job-tailor">\
                                <div class="btn btn-blue add-job-line"><i class="icon-plus"></i>添加行</div>\
                            </div>');
    var job_line_table = $('<table class="job-line-table" \
                                <thead> \
                                    <tr>\
                                    <td>Script Name</td>\
                                    <td>主机列表</td>\
                                    <td>备注</td>\
                                    </tr>\
                                    </thead> \
                                <tbody class="job-line-body"\>');

    job_header.appendTo(job_container);
    job_body.appendTo(job_container);
    job_tailor.appendTo(job_container);

    parent.html(job_container);

    job_line_table.appendTo(job_body);

    var job_detail_body = job_line_table.children(".job-line-body");
    //var selector = $("<div id='selector'/>");
    //selector.appendTo("body");
    var detail_row = 0;


    $(".add-job-line").click(function(){
        add_job_line()
    });

    Job.prototype.add_job_line = function(){
        add_job_line();
    };

    function save() {
        var o = {"job_name": $("input#job-name").val()};
        var lines = [];
        $.each(job_detail_body.children("tr"), function (index, value) {
            var job_line = {
                "script_id": $($(value).find("select.script-selector")).multipleSelect("getSelects").toString(),
                "desc": $($(value).find("input.job-line-desc")).val()
            };
            job_line.job_details = [];
            $.each($($(value).find("select.host-selector")).multipleSelect("getSelects").toString().split(","), function (index2, value2) {
                job_line.job_details[index2] = {"host_id": value2};
            });
            lines.push(job_line);
        });
        o.job_lines = lines;

        if (validate(o) == 0) {
            //do post to create job
            postJob(o);
        }
    }
    function add_job_line() {
        detail_row = detail_row + 1;
        var job_detail_row = $('<tr> \
            <td><select class="script-selector" multiple="multiple"/></td> \
            <td><select class="host-selector" multiple="multiple"/></td> \
            <td><input type="text" class="job-line-desc"></td> \
            </tr>');

        job_detail_row.attr("id", "detail_row_" + detail_row);
        job_detail_row.appendTo(job_detail_body);

        var ss = job_detail_row.find("select.script-selector")[0];
        showScriptSelector($(ss));

        var hs = job_detail_row.find("select.host-selector")[0];
        showHostSelector($(hs));
    }
    function validate(job) {
        var err_msg = "";
        if (typeof job.job_name === "undefined" || job.job_name == "") {
            err_msg = err_msg + "job name empty\n";
        }
        var lines = job.job_lines;
        if (lines.length == 0) {
            err_msg = err_msg + "no job lines\n";
        }
        $.each(lines, function (index, value){
            if (typeof value.script_id === "undefined" || value.script_id == "") {
                err_msg = err_msg + "script id is missing: line " + index + "\n";
            }
            $.each(value.job_details, function (index2, value2) {
                if (typeof value2.host_id === "undefined" || value2.host_id == "") {
                    err_msg = err_msg + "host id is missing: line " + index + " detail " + index2 + "\n";
                }
            })
        });

        if (err_msg != "") {
            alert(err_msg);
            return 1;
        } else {
            return 0;
        }
    }
}

function postJob(job){
    var data = JSON.stringify(job);
    $.post(job_service + "/" + "add", { "data":data }, function(data){
        if (typeof data.ret_code !== 'undefined') {
            if (data.ret_code != 0) {
                alert(data.ret_msg);
            }else{
                window.location.href="job";
            }
        }
    }, dataType="json");
}

function getJob(job, job_id){
    $.post(job_service + "/" + job_id, function(data){
        if (typeof data.ret_code !== 'undefined') {
            if (data.ret_code != 0) {
                alert(data.ret_msg);
            }else{
                //show job info
            }
        }
    }, dataType="json");
}

search("Job");


dialog = $( "#dialog-form" ).dialog({
    dialogClass: "fanui",
    autoOpen: false,
    height: 600,
    width: 800,
    modal: true,
    buttons: {
        "Save Job": function() {
            job.save();
        },
        Cancel: function() {
            dialog.dialog( "close" );
        }
    }
});

$( "#addInstance" ).click(function (){
    job = new Job($( "#dialog-form" ));
    job.add_job_line();
    dialog.dialog( "open" );
});