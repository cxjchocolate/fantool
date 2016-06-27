/**
 * Created by Дѓал on 2016/1/13.
 */
function formatDate(date){
    str_date = date.getFullYear() + "-";
    if (date.getMonth() < 9) {
        str_date = str_date + "0" + (date.getMonth() + 1);
    } else {
        str_date = str_date + (date.getMonth() + 1);
    }
    str_date = str_date + "-" + date.getDate();
    return str_date;
}

function search(keyword, startdate, enddate){
    $.get("/fanctl/search", { kw: keyword, startdate: startdate, enddate:enddate, type:"list" }, function(data){
        if (typeof data !== 'undefined') {
            $( ".search-result").html(data)
        }
    })
}

function selectorSearch(keyword, startdate, enddate, parent){
    $.get("/fanctl/search", { kw: keyword, startdate: startdate, enddate:enddate, type:"selector" }, function(data){
        if (typeof data !== 'undefined') {
            parent.html(data)
        }
    })
}