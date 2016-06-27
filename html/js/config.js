/**
 * Created by ¥Û–€ on 2016/1/16.
 */
var ws_url = 'ws://' + location.host + '/fanctl/soc';
var server = "http://" + location.host;
var app_info_service = server + "/fanctl/app/info";
var mem_flush_service = server + "/fanctl/mem/flush";
var mem_keys_service = server + "/fanctl/mem/keys";
var conf_service = server + '/fanctl/conf';
var script_service = server + '/fanctl/script';
var job_service = server + '/fanctl/job';
var server_service = server + '/fanctl/server';
var appdict_service = server + '/fanctl/apps';
var app_service = server + '/fanctl/app';
var host_service = server + '/fanctl/host';
var svn_log_service = server + '/fanctl/svn/log';
var day_gap = 24*60*60*1000; //1ÃÏ